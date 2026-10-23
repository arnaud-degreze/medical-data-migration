from typing import TypedDict
from collections.abc import Callable
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, InsertOne, UpdateOne
import pandas as pd
import os

# CLASS DEFINITION
class Admission(TypedDict):
    MedicalCondition: str
    DateOfAdmission: datetime
    Doctor: str
    Hospital: str
    InsuranceProvider: str
    BillingAmount: float
    RoomNumber: int
    AdmissionType: str
    DischargeDate: datetime
    Medication: str
    TestResults: str
    PatientId: ObjectId

class Patient(TypedDict):
    Name: str
    Gender: str
    BloodType: str
    Age: int

## MIGRATION FUNCTIONS
def to_admission(row) -> Admission:
    return {
        "PatientId": ObjectId(row["PatientId"]),
        "MedicalCondition": row["MedicalCondition"],
        "DateOfAdmission": row["DateOfAdmission"],
        "Doctor": row["Doctor"],
        "Hospital": row["Hospital"],
        "InsuranceProvider": row["InsuranceProvider"],
        "BillingAmount": row["BillingAmount"],
        "RoomNumber": row["RoomNumber"],
        "AdmissionType": row["AdmissionType"],
        "DischargeDate": row["DischargeDate"],
        "Medication": row["Medication"],
        "TestResults": row["TestResults"]
    }

def to_patient(row: dict) -> Patient:
    return {
        "Name": row["Name"],
        "Gender": row["Gender"],
        "BloodType": row["BloodType"],
        "Age": int(row["Age"])
    }


def patient_filter(row: dict) -> dict:
    return to_patient(row)

def admission_filter(row: dict) -> dict:
    return {
        "PatientId": row["PatientId"],
        "DateOfAdmission": row["DateOfAdmission"],
        "MedicalCondition": row["MedicalCondition"]
    }

def create_or_update_collection(
    df: pd.DataFrame,
    collection,
    build_filter: Callable[[dict], dict],
    build_document: Callable[[dict], dict]
) -> None:

    operations = []
    for row in df.to_dict("records"):
        filter = build_filter(row)
        document = build_document(row)


        operations.append(
            UpdateOne(
                filter,
                {'$setOnInsert': document},
                upsert=True
            )
        )

    if operations:
        results = collection.bulk_write(
            operations,
            ordered = False
        )

    print(f"Collection {collection.name} : ")
    print(f"{results.upserted_count} nouveaux documents insérés.")
    print(f"{results.matched_count} documents déjà existants.")


def build_patient_id_map(patients_df: pd.DataFrame,
                         patients_collection):


    records = patients_df.to_dict("records")
    patient_id_map = {}
    batch_size=500

    for start in range(0, len(records), batch_size):
        batch = records[start: start + batch_size]

        filters = [
            {
                "Name": row["Name"],
                "Age": int(row["Age"]),
                "Gender": row["Gender"],
                "BloodType": row["BloodType"]
            }
            for row in batch
        ]

        cursor = patients_collection.find(
            {"$or": filters},
            {
                "_id": 1,
                "Name": 1,
                "Age": 1,
                "Gender": 1,
                "BloodType": 1
            }
        )

        mongo_ids = {
            (
                doc["Name"],
                doc["Age"],
                doc["Gender"],
                doc["BloodType"]
            ):doc["_id"]
            for doc in cursor
        }

        for row in batch:
            key =  (
                row["Name"],
                int(row["Age"]),
                row["Gender"],
                row["BloodType"]
            )
            patient_id_map[row["PatientId"]]=mongo_ids[key]

    return patient_id_map



def ensure_indexes(collection):
    if collection.name == "patients":
        collection.create_index(
            [
                ("Name", 1),
                ("Age", 1),
                ("Gender", 1),
                ("BloodType", 1)
            ],
            unique = True,
            name = "unique_patient"
        )
    else:
        collection.create_index(
            [
                ("PatientId", 1),
                ("DateOfAdmission", 1),
                ("MedicalCondition", 1)
            ],
            unique =True,
            name = "unique_admission"
        )

def associate_patients_id_with_admissions(patient_id_map: dict,
                                           admissions_df: pd.DataFrame):
    admissions_df = admissions_df.copy()
    admissions_df["PatientId"] = admissions_df["PatientId"].map(patient_id_map)

    if admissions_df["PatientId"].isna().any():
        raise ValueError(
            "Certains PatientId n'ont pas été associés à un patient MongoDB."
        )
    return admissions_df



def migrate_data(patients_df: pd.DataFrame,
                 admissions_df: pd.DataFrame,
                 database_name: str =  "medical") -> None:

    uri = os.getenv("MONGODB_URI")
    database_name = os.getenv("MONGODB_DB_NAME")

    client = MongoClient(uri)
    print("Connexion établie au serveur MongoDB")

    try:
        database = client[database_name]
        print(f"Connecté à la base de donnée {database.name}")
        patients_collection = database["patients"]
        admissions_collection = database["admissions"]
        print(f"Connexion réussie aux collections {patients_collection.name} et {admissions_collection.name}")

        ensure_indexes(patients_collection)
        ensure_indexes(admissions_collection)

        print("Début de l'écriture des patients")
        create_or_update_collection(
             patients_df,
             patients_collection,
             build_filter=patient_filter,
             build_document=to_patient
        )
        print("Ecriture des patients terminée")

        patient_id_map = build_patient_id_map(patients_df, patients_collection)

        admissions_df = associate_patients_id_with_admissions(
            patient_id_map,
            admissions_df,
        )

        print("Début de l'écriture des admissions")
        create_or_update_collection(
            admissions_df,
            admissions_collection,
            build_filter=admission_filter,
            build_document=to_admission
        )
        print("Ecriture des admissions terminées")

    except Exception as e:
        raise Exception(
            "The following exception occurred: ", e)

    finally:
        client.close()
        print("Connexion au serveur MongoDB clôturée")

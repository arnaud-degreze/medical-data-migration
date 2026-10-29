from typing import TypedDict
from collections.abc import Callable
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, InsertOne, UpdateOne
from pymongo.collection import Collection
import pandas as pd
import os

# CLASSES DEFINITION
class Admission(TypedDict):
    """ Class declares explicit types for MongoDB """
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
    """ Class declares explicit types for MongoDB """
    Name: str
    Gender: str
    BloodType: str
    Age: int


## HELPERS
def to_admission(row: dict) -> Admission:
    """ Return the document typed with the Admission class """
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
    """ Return the document typed with the Patient class """
    return {
        "Name": row["Name"],
        "Gender": row["Gender"],
        "BloodType": row["BloodType"],
        "Age": int(row["Age"])
    }


def patient_filter(row: dict) -> dict:
    """
    Returns the entire row.

    Author's note:
    The patient filter - or composite key - is made of the entire patient record (except the PatientId).
    The function might seem silly since entry and return are the same, but it was made to keep consistency when
    the create_or_update_collection function is called.
    In doing so, the call is identical in arguments declaration whether it is for Admission or Patient.
    """
    return to_patient(row)

def admission_filter(row: dict) -> dict:
    """
    Returns the Admission filter as a dict.
    """
    return {
        "PatientId": row["PatientId"],
        "DateOfAdmission": row["DateOfAdmission"],
        "MedicalCondition": row["MedicalCondition"]
    }


# SECONDARY FUNCTIONS
def create_or_update_collection(
    df: pd.DataFrame,
    collection: Collection,
    build_filter: Callable[[dict], dict],
    build_document: Callable[[dict], dict]
) -> None:
    """
    Inject or update documents inside MongoDB collection

    Requirements:
    - non-empty DataFrame.

    Author's note:
    The simplest method I found to write my data while checking if it existed before was to use an UpdateOne
    instruction for every patient/admission. If the document is present inside, nothing is done, else it is
    upserted (= insert). However, the  MongoDB server is  called for each UpdateOne instruction, so a
    bulk_write was used to reduce the number of server calls.

    Another option would have been to insert only the new documents. But to do that, I would have needed
    to load the collection. For a large collection, it could overload my memory - so I chose the first option.
    """

    if df.empty:
        print(f"Collection {collection.name} :")
        print("Aucun document à traiter.")
        return

    operations = []

    for row in df.to_dict("records"):
        filter = build_filter(row)
        document = build_document(row)

        operations.append(
            UpdateOne(
                filter,
                {"$setOnInsert": document},
                upsert=True,
            )
        )

    results = collection.bulk_write(operations, ordered=False)

    print(f"Collection {collection.name} :")
    print(f"{results.upserted_count} nouveaux documents insérés.")
    print(f"{results.matched_count} documents déjà existants.")

def build_patient_id_map(
    patients_df: pd.DataFrame,
    patients_collection: Collection
) -> dict[ObjectId, ObjectId]:

    """
    Returns a dict object with the temporary ObjectId as key, and the MongoDB _id as the value.

    Author's note:
    Before, we had unique patients and admissions linked by a temporary ObjectId inside our data.
    Now, we want to link the temporary id to the MongoDB id. To do that, we load every MongoDB entries
    that are in our DataFrame and use a key (tuple) to make the link between the two IDs.

    Since the data can be voluminous, we batch the process, by only using 500 patients at a time.
    """

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


def associate_patients_id_with_admissions(
    patient_id_map: dict[ObjectId, ObjectId],
    admissions_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Map the MongoDB id to the temporary id present in the data.

    Requirement:
    - Every temporary id should have a MongoDB equivalent.
    """
    admissions_df = admissions_df.copy()
    admissions_df["PatientId"] = admissions_df["PatientId"].map(patient_id_map)

    if admissions_df["PatientId"].isna().any():
        raise ValueError(
            "Certains PatientId n'ont pas été associés à un patient MongoDB."
        )
    return admissions_df


def ensure_indexes(collection: Collection) -> None:
    """
    Create or ensure indexes on each collection.

    Author's Note:
    They key to identifying a patient is a mixture of all its attributes.
    For an admission, the PatientId, its admission date and its medical condition are enough
    to make it unique.
    As such, indexes will be created on each of these attributes.
    """
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


# MAIN FUNCTION TO BE CALLED
def migrate_data(
    patients_df: pd.DataFrame,
    admissions_df: pd.DataFrame,
    database_name: str = 'medical'
) -> None:

    """
    INTEGRATION FUNCTION - makes the migration happens.

    Requirements:
    - ENV variables available in the .env and declared in the environment instruction of the migration service.
    """

    uri = os.getenv("MONGODB_URI")

    if database_name == os.getenv("MONGODB_MIGRATION_DB_NAME"):
        username = os.getenv("MONGO_MIGRATION_USERNAME")
        password = os.getenv("MONGO_MIGRATION_PASSWORD")
    else:
        username = os.getenv("MONGO_TESTER_USERNAME")
        password = os.getenv("MONGO_TESTER_PASSWORD")

    client = MongoClient(
        uri,
        username = username,
        password = password,
        authSource = database_name
    )
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

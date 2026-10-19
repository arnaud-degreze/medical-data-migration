from typing import TypedDict
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, InsertOne
import pandas as pd

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

def to_patient(row) -> Patient:
    return {
        "Name": row["Name"],
        "Gender": row["Gender"],
        "BloodType": row["BloodType"],
        "Age": row["Age"]
    }


## HELPER


def migrate_patients(patients: pd.DataFrame):
    try:
        uri = "mongodb://localhost:27017/"
        client = MongoClient(uri)
        print("Connexion établie au serveur MongoDB - port : 27017")

        database = client["medical"]
        collection = database["patients"]
        print('Connectée à la collection "patients" de la database "medical"')

        operations = [InsertOne(to_patient(row)) for index, row in patients.iterrows()]

        res = collection.bulk_write(operations)

        print(f'Ecriture dans la collection "patients" terminée ?', res.acknowledged)

        print(f"{len(operations)} documents ont été écrits")
        client.close()
        print("Connexion clôturée")

    except Exception as e:
        raise Exception(
            "The following exception occurred: ", e)


def migrate_admissions(admissions: pd.DataFrame):
    try:
        uri = "mongodb://localhost:27017/"
        client = MongoClient(uri)
        print("Connexion établie au serveur MongoDB - port : 27017")

        database = client["medical"]
        collection = database["admissions"]
        print('Connectée à la collection "admissions" de la database "medical"')

        operations = [InsertOne(to_admission(row)) for index, row in admissions.iterrows()]

        res = collection.bulk_write(operations)

        print(f'Ecriture dans la collection "admissions" terminée ?', res.acknowledged)

        print(f"{len(operations)} documents ont été écrits")
        client.close()
        print("Connexion clôturée")

    except Exception as e:
        raise Exception(
            "The following exception occurred: ", e)

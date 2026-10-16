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
        "MedicalCondition": str(row["MedicalCondition"]),
        "DateOfAdmission": convert_to_datetime(row["DateOfAdmission"]),
        "Doctor": str(row["Doctor"]),
        "Hospital": str(row["Hospital"]),
        "InsuranceProvider": str(row["InsuranceProvider"]),
        "BillingAmount": float(row["BillingAmount"]),
        "RoomNumber": int(row["RoomNumber"]),
        "AdmissionType": str(row["AdmissionType"]),
        "DischargeDate": convert_to_datetime(row["DischargeDate"]),
        "Medication": str(row["Medication"]),
        "TestResults": str(row["TestResults"])
    }

def to_patient(row) -> Patient:
    return {
        "Name": str(row["Name"]),
        "Gender": str(row["Gender"]),
        "BloodType": str(row["BloodType"]),
        "Age": int(row["Age"])
    }


## HELPER
def convert_to_datetime(date_str: str):
    format = '%Y-%m-%d'
    datetime_str = datetime.strptime(date_str, format)
    return datetime_str


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

        client.close()
        print("Connexion clôturée")

    except Exception as e:
        raise Exception(
            "The following error occurred: ", e)


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

        client.close()
        print("Connexion clôturée")

    except Exception as e:
        raise Exception(
            "The following error occurred: ", e)

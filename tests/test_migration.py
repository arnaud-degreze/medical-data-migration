import os
import pytest
import pandas as pd
from medical_migration.migration import (
    to_patient,
    to_admission,
    associate_patients_id_with_admissions,
    migrate_data
)
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient

@pytest.fixture
def test_data():
    patient_id = ObjectId()
    admission_date = datetime(2025, 1, 10)
    discharge_date = datetime(2025, 1, 15)

    return {
        "Name": "Jean Dupont",
        "Gender": "Male",
        "BloodType": "AB+",
        "Age": 42,
        "PatientId": patient_id,
        "MedicalCondition": "Diabetes",
        "DateOfAdmission": admission_date,
        "Doctor": "Dr Martin",
        "Hospital": "San Juan",
        "InsuranceProvider": "Franco&Co",
        "BillingAmount": 1200.0,
        "RoomNumber": 101,
        "AdmissionType": "AlmostTooLate",
        "DischargeDate": discharge_date,
        "Medication": "ChocolateBar",
        "TestResults": "Excellent"
    }

def test_to_patient(test_data):
    row = {
        "Name": test_data["Name"],
        "Gender": test_data["Gender"],
        "BloodType": test_data["BloodType"],
        "Age": test_data["Age"],
    }

    result = to_patient(row)

    assert result == {
        "Name": "Jean Dupont",
        "Gender": "Male",
        "BloodType": "AB+",
        "Age": 42,
    }
    assert isinstance(result["Age"], int)


def test_to_admission(test_data):
    row = {
        "PatientId": test_data["PatientId"],
        "MedicalCondition": test_data["MedicalCondition"],
        "DateOfAdmission": test_data["DateOfAdmission"],
        "Doctor": test_data["Doctor"],
        "Hospital": test_data["Hospital"],
        "InsuranceProvider": test_data["InsuranceProvider"],
        "BillingAmount": test_data["BillingAmount"],
        "RoomNumber": test_data["RoomNumber"],
        "AdmissionType":test_data["AdmissionType"],
        "DischargeDate": test_data["DischargeDate"],
        "Medication": test_data["Medication"],
        "TestResults": test_data["TestResults"]
    }

    result = to_admission(row)

    assert result["PatientId"] == row["PatientId"]
    assert result["DateOfAdmission"] ==  row["DateOfAdmission"]
    assert result["DischargeDate"] == row["DischargeDate"]
    assert result["MedicalCondition"] == row["MedicalCondition"]


def test_associate_patient_ids():
    temporary_id = "patient_temp_id"
    mongo_id = ObjectId()

    admissions_df = pd.DataFrame({
        "PatientId": [temporary_id, temporary_id],
        "MedicalCondition": ["Diabetes", "Asthme"],
    })

    result = associate_patients_id_with_admissions(
        {temporary_id: mongo_id},
        admissions_df,
    )

    assert result["PatientId"].tolist() == [mongo_id, mongo_id]



def test_associate_patient_ids_raises_if_missing():
    admissions_df = pd.DataFrame({
        "PatientId": ["unknown"]
    })

    with pytest.raises(ValueError, match="pas été associé"):
        associate_patients_id_with_admissions(
            {},
            admissions_df
        )

def test_idempotence_migration(test_data):
    uri = os.getenv("MONGODB_URI")
    username = os.getenv("MONGO_TESTER_USERNAME")
    password = os.getenv("MONGO_TESTER_PASSWORD")
    database_name = os.getenv("MONGODB_TEST_DB_NAME")

    test_df=pd.DataFrame([test_data])

    patients_df = test_df[["PatientId", "Name", "Age", "Gender", "BloodType"]]
    admissions_df = test_df[[
        "PatientId",
        "MedicalCondition",
        "DateOfAdmission",
        "Doctor",
        "Hospital",
        "InsuranceProvider",
        "BillingAmount",
        "RoomNumber",
        "AdmissionType",
        "DischargeDate",
        "Medication",
        "TestResults"
    ]]

    print("uri: ", uri),
    print("username: ", username)
    print("authSource: ", database_name)

    client = MongoClient(
        uri,
        username = username,
        password = password,
        authSource = database_name
    )

    try:
        client.drop_database(database_name)
    finally:
        client.close()

    # Première migration avec les données à tester
    migrate_data(
        patients_df,
        admissions_df,
        database_name)


    client = MongoClient(
        uri,
        username = username,
        password = password,
        authSource = database_name
    )
    try:
        db = client[database_name]
        patients_before = db["patients"].count_documents({})
        admissions_before = db["admissions"].count_documents({})

        # Deuxième migration avec les mêmes données
        migrate_data(
            patients_df,
            admissions_df,
            database_name,
        )

        assert db["patients"].count_documents({}) == patients_before
        assert db["admissions"].count_documents({}) == admissions_before

        assert patients_before == 1
        assert admissions_before == 1

    finally:
        client.drop_database(database_name)
        client.close()

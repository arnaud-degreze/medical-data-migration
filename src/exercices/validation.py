import pandas as pd

def validate_data(df: pd.DataFrame) -> pd.DataFrame:

    dtype_map = {
        "Name": "string",
        "Gender": "string",
        "Age": "int64",
        "BloodType": "string",
        "MedicalCondition": "string",
        "Doctor": "string",
        "Hospital": "string",
        "InsuranceProvider": "string",
        "BillingAmount": "float64",
        "RoomNumber": "int64",
        "AdmissionType": "string",
        "Medication": "string",
        "TestResults": "string"
    }

    df = df.astype(dtype_map)

    df["DateOfAdmission"] = pd.to_datetime(
        df["DateOfAdmission"],
        errors="raise"
    )

    df["DischargeDate"] = pd.to_datetime(
        df["DischargeDate"],
        errors="raise"
    )

    pass

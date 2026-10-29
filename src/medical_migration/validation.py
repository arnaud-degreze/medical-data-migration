import pandas as pd

def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Return a DataFrame with its types fixed.

    Requirement:
    - DateOfAdmission/DischargeDate  must be of the form %Y-%m-%d (e.g. 2026-10-24), else an Error is raised
    - Values should be convertible to the fixed type, else an Error would be raised.

    Author's note :
    While the type is fixed, it does not guarantee consistency with the values itself.
    Example : Bloodtype could well be '456'.
    An improvement would be to check values for nominal attributes (Gender, BloodType, etc...),
    as well as discrete quantitative attributes (Age).
    """

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
        format="%Y-%m-%d",
        errors="raise"
    )

    df["DischargeDate"] = pd.to_datetime(
        df["DischargeDate"],
        format="%Y-%m-%d",
        errors="raise"
    )

    return df

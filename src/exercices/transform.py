import pandas as pd
from bson import ObjectId

def normalize_name(full_name : str) -> str:
    if not isinstance(full_name, str) or not full_name.strip():
        raise ValueError("Nom absent ou invalide")

    parts = full_name.strip().split()

    titles = {"mr", "mrs", "ms", "miss", "dr"}
    suffixes = {"jr", "sr"}

    if parts and parts[0].rstrip(".").casefold() in titles:
        parts.pop(0)

    if parts and parts[-1].rstrip(".").casefold() in suffixes:
        parts.pop()

    if len(parts) < 2:
        raise ValueError(f"Nom ambigu : {value!r}")

    first_name = parts[0].casefold()
    last_name = " ".join(parts[1:]).casefold()

    return first_name, last_name


def build_patient_key(row) -> tuple: 
    return (
        normalize_name(row["Name"]),
        int(row["Age"]),
        str(row["Gender"]),
        str(row["BloodType"])
    )

patient_ids = {}

def get_patient_id(row):
    key = build_patient_key(row)

    if key not in patient_ids:
        patient_ids[key] = ObjectId()

    return patient_ids[key]


def split_dataframe(df: pd.DataFrame) -> pd.DataFrame :
    patient_columns = [
        "PatientId",
        "Name",
        "Age",
        "Gender",
        "BloodType"
    ]

    patient_df = (
        df[patient_columns]
        .drop_duplicates(subset=['PatientId'])
        .copy()
    ).reset_index(drop=True)

    admission_df = df.drop(
        columns=["Name", "Age", "Gender", "BloodType"]
    ).copy()

    return patient_df, admission_df

def transform_data(df: pd.DataFrame) -> pd.DataFrame:

    print("Attribution d'un identifiant unique en cours")

    df["PatientId"] = df.apply(get_patient_id, axis=1)

    print("Attribution des identifiants terminés")

    print("Création des DataFrame Patients et Admissions en cours")

    return  split_dataframe(df)


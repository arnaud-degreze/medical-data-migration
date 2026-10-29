import pandas as pd
import re
from bson import  ObjectId

## FUNCTIONS

def format_header(header: list[str]) -> list[str]:
    """
    Returns a list of formatted strings.

    Keywords:
    - header: list of strings

    Format process:
    - Split initial col name into separate words
    - Capitalize each words
    - Join each words together with whitespace removal
    Ex : 'initial String' -> 'InitialString'
    """
    return [
        "".join(word.capitalize() for word in col.split())
        if " " in col else col
        for col in header
    ]

def filter_null_values(df:pd.DataFrame):
    """Returns a DataFrame copy exempt of null values on key attributes."""

    non_null_cols = ["Name", "Gender", "Age", "BloodType", "DateOfAdmission", "MedicalCondition"]

    values = df[non_null_cols]

    #Null values are either isna() or whitespaced strings.
    mask = (
        values.isna()
        | values.astype("string").apply(
            lambda col: col.str.strip().eq("")
        )
    ).any(axis=1)

    return df.loc[~mask].copy()

def normalize_name(full_name : str) -> str:
    """
    Returns a formatted string.

    Keywords:
    - full_name: str

    Requirements:
    - Keyword is a string, else ValueError is raised.
    - Keyword is not empty or whitespaced only, else ValueError is raised.
    - Keyword is at least constituted of a first name and last name separated by a whitespace,
        else ValueError is raised.
    """

    if not isinstance(full_name, str) or not full_name.strip():
        raise ValueError("Nom absent ou invalide")

    #Removal of trailing and ending whitespace, then splitting
    parts = full_name.strip().split()

    titles = {"mr", "mrs", "ms", "miss", "dr"}
    suffixes = {"jr", "sr"}

    #Removal of prefixes/titles
    if parts and parts[0].rstrip(".").casefold() in titles:
        parts.pop(0)

    #Removal of suffixes
    if parts and parts[-1].rstrip(".").casefold() in suffixes:
        parts.pop()

    if len(parts) < 2:
        raise ValueError(f"Nom ambigu : {value!r}")

    #First name and last name conversion to lowercase
    first_name = parts[0].casefold()
    last_name = " ".join(parts[1:]).casefold()

    return first_name + " " + last_name


def drop_duplicates_w_criterias(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame without duplicates. No inplace modifications.

    Author's note :
    The below criterias are arbitrary criterias that, if identical for at least two admissions,
    suggest an admission is duplicated. In effect, the logic is described below.
    If two persons or more are caracterized by :
    - The same name.
    - The same gender.
    - The same bloodtype.
    And have an admission where they were :
    - Admitted on the same day
    - Discharged on the same day.
    - In the same hospital.
    - In the same room.
    - Have received the same medication.
    - Need to pay the same amount.
    Then it is reasonable to think the admission is duplicated.
    """

    criterias = [
        "Name", "Gender",
        "DateOfAdmission", "DischargeDate",
        "BloodType", "BillingAmount",
        "RoomNumber", "Medication",
        "Hospital"
    ]

    df = df[~df[criterias].duplicated(keep=False)].reset_index(drop=True)

    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Returns a DataFrame :
    - with a formatted header.
    - free of null-values on key columns.
    - without admission duplicates.
    """
    print('Renommage du header et des valeurs de l\'attribut "Name"')

    df.columns = format_header(df.columns)
    print("Suppression des valeurs nulles")
    df = filter_null_values(df)

    df["Name"] = df["Name"].apply(normalize_name)

    print("Suppression des doublons simples en cours")

    df_wo_doublons = drop_duplicates_w_criterias(df)

    print(f"La suppression des doublons simples a occasionné {len(df) - len(df_wo_doublons)} lignes supprimées.\n"
      f"Environ {round((len(df) - len(df_wo_doublons)) / len(df) * 100,1)}% du fichier a donc été affecté.")

    return df_wo_doublons




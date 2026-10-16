import pytest
import pandas as pd
from exercices.transforming import normalize_name, get_patient_id, split_dataframe

@pytest.fixture
def df_test_patient_key():
    return pd.DataFrame({
        "Name": ["Bobby Jackson", "Danny SMITH", "danny Smith", "andrew Wats"],
        "Age": [30, 76, 76, 28],
        "Gender": ["Male", "Female", "Female", "Female"],
        "BloodType": ["B+", "A+", "A+", "O+"]
    })

@pytest.fixture
def df_test_for_splitting():
    return pd.DataFrame({
        "Name": ["Bobby Jackson", "Danny SMITH", "danny Smith", "andrew Wats"],
        "Age": [30, 76, 76, 28],
        "Gender": ["Male", "Female", "Female", "Female"],
        "BloodType": ["B+", "A+", "A+", "O+"],
        "PatientId": [1, 2, 2, 3],
        "InsuranceProvider": ["ParisCo", "LyonCo", "MontpellierCO", "TrunbrCo"],
        "Medication": ["Food", "Aspirin", "Ibuprofene", "Chocolat"]
    })


def test_incorrect_full_name():
    with pytest.raises(ValueError) as e_info:
        assert normalize_name("   ")
        assert normalize_name(45)
        assert normalize_name("Jean")


def test_duplicate_patient(df_test_patient_key):
    df_test_patient_key["PatientId"] = df_test_patient_key.apply(get_patient_id, axis=1)
    result = df_test_patient_key["PatientId"].drop_duplicates()
    assert len(result) == 3


def test_split_dataframe(df_test_for_splitting):
    df1, df2 = split_dataframe(df_test_for_splitting)
    patients_cols = ["Name", "Gender", "Age", "BloodType", "PatientId"]

    is_patients_cols_not_in_df2 = [True for col in patients_cols
           if (col not in df2.columns) & (col != "PatientId")]
    is_patient_id_present_in_both = ("PatientId" in df1.columns) & ("PatientId" in df2.columns)

    is_patients_cols_in_df1 = [True for col in patients_cols
           if col in df1.columns]

    assert all(is_patients_cols_not_in_df2)
    assert is_patient_id_present_in_both
    assert (all(is_patients_cols_in_df1)) & (len(patients_cols) == len(df1.columns))

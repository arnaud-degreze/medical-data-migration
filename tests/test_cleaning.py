from exercices.cleaning import format_header, filter_null_values, clean_data
import pytest
import pandas as pd


@pytest.fixture
def list_test_format_header():
    return [
        "TEST", "TE ST", "teST", "te  st"
    ]

@pytest.fixture
def df_test_missing_values():
    return pd.DataFrame({
        "Name": ["Alice", "Bob", None, "David", "Emma"],
        "Gender": ["Female", "Male", "Female", None, "Female"],
        "Age": [25, 30, 40, 35, None],
        "BloodType": ["A+", "O+", "B+", "AB+", ""],
        "PatientId": [1, 2, 3, 4, 5]
    })


@pytest.fixture
def df_test_for_idempotence():
    return pd.DataFrame({
        "Name": ["Bobby Jackson", "Danny SMITH", "danny Smith", "DANNY SMITH"],
        "Age": [30, 76, 76, 28],
        "Gender": ["Male", "Female", "Female", "Male"],
        "Blood Type": ["B+", "A+", "A+", "O+"],
        "Patient Id": [1, 2, 2, 3],
        "Insurance Provider": ["ParisCo", "LyonCo", "MontpellierCO", "TrunbrCo"],
        "Medication": ["Food", "Aspirin", "Aspirin", "Chocolat"],
        "Billing Amount": [12.5, 15, 15, 17],
        "Room Number": [123, 320, 320, 236],
        "Hospital": ["H&H", "GrP", "GrP", "San Antonio"],
        "Date Of Admission": ["2020-11-17", "2021-06-12", "2021-06-12", "2019-02-24"],
        "Discharge Date": ["2023-11-16", "2023-11-16", "2023-11-16", "2023-11-16"]
    })

def test_format_header(list_test_format_header):
    result = format_header(list_test_format_header)
    res = [True for text in result
           if text == "Test"]
    assert all(res)

def test_filter_null_values(df_test_missing_values):
    result = filter_null_values(df_test_missing_values)
    assert len(result) == 2

def test_no_missing_values_in_required_columns(df_test_missing_values):
    result=filter_null_values(df_test_missing_values)

    required_cols = ["Name", "Gender", "Age", "BloodType"]

    assert not result[required_cols].isna().any().any()
    assert not result[required_cols].eq("").any().any()


def test_idempotence_process(df_test_for_idempotence):
    df_cleaned = clean_data(df_test_for_idempotence)
    res = clean_data(df_cleaned)
    assert  df_cleaned.equals(res)


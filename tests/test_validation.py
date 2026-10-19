import pytest
import pandas as pd
from exercices.validation import validate_data


@pytest.fixture
def df_test_date_type():
    return pd.DataFrame({
        "Name": ["Bobby Jackson", "Danny SMITH", "danny Smith", 64],
        "Age": [30, 76, 76, 28],
        "Gender": ["Male", "Female", "Female", "Male"],
        "BloodType": ["B+", "A+", "A+", "O+"],
        "InsuranceProvider": ["ParisCo", "LyonCo", "MontpellierCO", "TrunbrCo"],
        "Medication": ["Food", "Aspirin", "Aspirin", "Chocolat"],
        "BillingAmount": [12.5, 15, 15, 17],
        "RoomNumber": [123, 320, 320, 236],
        "Hospital": ["H&H", "GrP", "GrP", "San Antonio"],
        "DateOfAdmission": ["20201117", "20210612", "20210612", "20190224"],
        "DischargeDate": ["20231116", "20231116", "20231116", "20231116"],
        "MedicalCondition": ["Cancer", "Obesity", "TooMuchChocolate", "Gulping"],
        "Doctor": ["Lopez", "Gru", "Michelin", "Gandalf"],
        "TestResults": ["Negative", "Remission", "Guilty", "WhatElse?"],
        "AdmissionType" : ["Urgent", "Urgent", "BottomList", "Negligent"]
    })

@pytest.fixture
def df_test_date_type_2():
    return pd.DataFrame({
        "Name": ["Bobby Jackson", "Danny SMITH", "danny Smith", 64],
        "Age": [30, 76, 76, 28],
        "Gender": ["Male", "Female", "Female", "Male"],
        "BloodType": ["B+", "A+", "A+", "O+"],
        "InsuranceProvider": ["ParisCo", "LyonCo", "MontpellierCO", "TrunbrCo"],
        "Medication": ["Food", "Aspirin", "Aspirin", "Chocolat"],
        "BillingAmount": [12.5, 15, 15, 17],
        "RoomNumber": [123, 320, 320, 236],
        "Hospital": ["H&H", "GrP", "GrP", "San Antonio"],
        "DateOfAdmission": ["2020/11-17", "2021.06.12", "2021-06-12", "2019-02-24"],
        "DischargeDate": ["2023-11-16", "2023-11-16", "2023-11-16", "2023-11-16"],
        "MedicalCondition": ["Cancer", "Obesity", "TooMuchChocolate", "Gulping"],
        "Doctor": ["Lopez", "Gru", "Michelin", "Gandalf"],
        "TestResults": ["Negative", "Remission", "Guilty", "WhatElse?"],
        "AdmissionType" : ["Urgent", "Urgent", "BottomList", "Negligent"]
    })



def test_type_validation(df_test_date_type):
    with pytest.raises(ValueError):
        assert validate_data(df_test_date_type)
        assert validate_data(df_test_date_type_2)

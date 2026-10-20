import pytest
import pandas as pd

from exercices.loading import load_data

def test_missing_file():
    with pytest.raises(FileNotFoundError):
        assert  load_data("fichier_inexistant.csv")

def test_output_type():
    df = load_data("tests/test_files/test_data_output.csv")
    assert isinstance(df, pd.DataFrame)

def test_empty_file():
    with pytest.raises(Exception) as e_info:
        assert load_data("tests/test_files/test_empty_file.csv")

def test_missing_cols():
    with pytest.raises(Exception) as e_info:
        assert load_data("tests/test_files/test_missing_col.csv")
        	

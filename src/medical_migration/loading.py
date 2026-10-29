import pandas as pd

def load_data(path : str) -> pd.DataFrame:
    """
    Read a CSV from its path into a DataFrame

    Keywords:
    - path : The CSV path in str format.

    Requirements:
    - Non-empty, so header and at least one line/entry, else an Exception is raised.
    - Complete header, any missing column will return an Exception.
    """

    required_cols = [
        "Name",
	"Age",
 	"Gender",
	"Blood Type",
	"Medical Condition",
	"Date of Admission",
	"Doctor",
	"Hospital",
	"Insurance Provider",
	"Billing Amount",
	"Room Number",
	"Admission Type",
	"Discharge Date",
	"Medication",
	"Test Results"
    ]

    df = pd.read_csv(path)

    if  len(df) == 0:
        raise Exception("Empty file not accepted")

    missing_cols = [
        col for col in required_cols
        if col not in df.columns
    ]

    if missing_cols:
        raise Exception(f"These columns are absent : {missing_cols}")

    return df


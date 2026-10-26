import pandas as pd

def load_data(path : str) -> pd.DataFrame:
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


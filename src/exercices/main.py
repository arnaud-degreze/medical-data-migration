from loading import load_data
from cleaning import clean_data
from validation import validate_data
from transform import transform_data
from migration import migrate_data
from pathlib import Path




def main():

    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / "data" / "admissions.csv"
    print("------ CHARGEMENT DES DONNEES ------")
    df = load_data("./data/healthcare_dataset.csv")
    print("------ CHARGEMENT TERMINE ------")

    print("------ DEBUT DU NETTOYAGE ------")
    clean_df = clean_data(df)
    print("------ NETTOYAGE TERMINE ------")

    print("------ DEBUT DE LA VALIDATION ------")
    validate_df = validate_data(clean_df)
    print("------ VALIDATION TERMINEE ------")

    print("------ DEBUT DE LA TRANSFORMATION ------")
    patients_df, admissions_df = transform_data(clean_df)
    print("------ TRANSFORMATION TERMINEE ------")

    print("------ DEBUT DE LA MIGRATION ------")
    migrate_data(patients_df, admissions_df)
    print("------ FIN DE LA MIGRATION ------")

if __name__ == "__main__":
    main()

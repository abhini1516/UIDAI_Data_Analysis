import pandas as pd
import numpy as np
import os
from glob import glob

# -----------------------------
# CONFIGURATION
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data_raw")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")

ENROL_DIR = os.path.join(DATA_DIR, "enrolment_zip")
DEMO_DIR = os.path.join(DATA_DIR, "demographic_zip")
BIO_DIR = os.path.join(DATA_DIR, "biometric_zip")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# SMART DATA LOADER (CSV + EXCEL)
# -----------------------------
def load_data_folder(folder_path):
    files = glob(os.path.join(folder_path, "*.csv")) + glob(os.path.join(folder_path, "*.xlsx"))

    if len(files) == 0:
        raise Exception(f"No CSV or Excel files found in {folder_path}")

    df_list = []

    for file in files:
        print(f"Loading: {file}")
        if file.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        df_list.append(df)

    combined = pd.concat(df_list, ignore_index=True)
    return combined

# -----------------------------
# CLEANING FUNCTION
# -----------------------------
def clean_dataframe(df):
    # Standardize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    # Remove duplicates
    df = df.drop_duplicates()

    # Replace common missing indicators with NaN
    df = df.replace(["NA", "N/A", "-", ""], np.nan)

    return df

# -----------------------------
# LOAD DATA
# -----------------------------
print("\nLoading Enrolment Data...")
enrol_df = load_data_folder(ENROL_DIR)

print("\nLoading Demographic Update Data...")
demo_df = load_data_folder(DEMO_DIR)

print("\nLoading Biometric Update Data...")
bio_df = load_data_folder(BIO_DIR)

# -----------------------------
# CLEAN DATA
# -----------------------------
enrol_df = clean_dataframe(enrol_df)
demo_df = clean_dataframe(demo_df)
bio_df = clean_dataframe(bio_df)

# -----------------------------
# BASIC VALIDATION
# -----------------------------
print("\nEnrolment Data Shape:", enrol_df.shape)
print("Demographic Data Shape:", demo_df.shape)
print("Biometric Data Shape:", bio_df.shape)

# -----------------------------
# EXPORT MASTER FILES
# -----------------------------
enrol_df.to_csv(os.path.join(OUTPUT_DIR, "enrolment_master_clean.csv"), index=False)
demo_df.to_csv(os.path.join(OUTPUT_DIR, "demographic_master_clean.csv"), index=False)
bio_df.to_csv(os.path.join(OUTPUT_DIR, "biometric_master_clean.csv"), index=False)

# -----------------------------
# CREATE TREND TABLES
# -----------------------------
if "state" in enrol_df.columns:
    enrol_trend = enrol_df.groupby("state").size().reset_index(name="total_enrolments")
    enrol_trend.to_csv(os.path.join(OUTPUT_DIR, "enrolment_trends.csv"), index=False)

if "state" in demo_df.columns:
    demo_trend = demo_df.groupby("state").size().reset_index(name="total_updates")
    demo_trend.to_csv(os.path.join(OUTPUT_DIR, "demographic_trends.csv"), index=False)

if "state" in bio_df.columns:
    bio_trend = bio_df.groupby("state").size().reset_index(name="total_biometric_updates")
    bio_trend.to_csv(os.path.join(OUTPUT_DIR, "biometric_trends.csv"), index=False)

print("\nPIPELINE COMPLETED SUCCESSFULLY")
print("Clean datasets saved in outputs folder")


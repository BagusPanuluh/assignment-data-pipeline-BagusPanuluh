from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_PATH = BASE_DIR / "data" / "raw" / "automobileEDA_dirty_training.csv"
PROCESSED_PATH = BASE_DIR / "data" / "processed" / "automobileEDA_processed_final.csv"

FREQUENCY_ENCODING_COLS = ["make", "engine-type", "fuel-system"]
ONE_HOT_COLS = ["body-style", "drive-wheels"]
LABEL_ENCODING_COLS = ["aspiration", "engine-location", "horsepower-binned"]


# Baca dataset
def load_data(filepath: Path) -> pd.DataFrame:
    data = pd.read_csv(filepath)
    return data


# Info dataset
def inspect_data(data: pd.DataFrame, label: str = "Dataset") -> None:
    print(f"\n===== Pemeriksaan Awal: {label} =====")

    print("\n-- 5 Baris Pertama --")
    print(data.head())

    print(f"\n-- Ukuran Dataset -- \n{data.shape[0]} baris, {data.shape[1]} kolom")

    print("\n-- Nama & Tipe Data Kolom --")
    print(data.dtypes)

    print("\n-- Jumlah Missing Values per Kolom --")
    missing = data.isnull().sum()
    print(missing[missing > 0] if missing.sum() > 0 else "Tidak ada missing values")

    print(f"\n-- Jumlah Duplicate Records -- \n{data.duplicated().sum()}")

    print("\n-- Nilai Unik pada Kolom Kategorikal yang Relevan --")
    categorical_cols = data.select_dtypes(include="object").columns
    for col in categorical_cols:
        print(f"{col}: {data[col].unique()}")


def get_column_types(data: pd.DataFrame):
    categorical_column = list(data.select_dtypes(include="object").columns)
    numerical_column = list(data.select_dtypes(include="number").columns)
    return categorical_column, numerical_column


# Cleansing
def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    data_clean = data.copy()

    n_before = len(data_clean)
    missing_before = data_clean.isnull().sum().sum()

    categorical_column, _ = get_column_types(data_clean)

    # Menyeragamkan penulisan kategori & menghapus spasi tidak perlu
    for col in categorical_column:
        data_clean[col] = data_clean[col].astype("str").str.lower().str.strip()

    # Memperbaiki tipe data yang belum sesuai
    if "transaction_date" in data_clean.columns:
        data_clean["transaction_date"] = pd.to_datetime(
            data_clean["transaction_date"], dayfirst=True, format="mixed", errors="coerce"
        )

    # Menghapus duplicate records
    n_dupe = data_clean.duplicated().sum()
    data_clean = data_clean.drop_duplicates()

    # Menangani missing values - kategorikal diisi modus
    for col in categorical_column:
        if data_clean[col].isnull().sum() > 0:
            data_clean[col] = data_clean[col].fillna(data_clean[col].mode()[0])

    # Menangani missing values - numerik diisi median/mean sesuai kondisi
    for col in ["stroke", "bore", "compression-ratio", "peak-rpm"]:
        if col in data_clean.columns and data_clean[col].isnull().sum() > 0:
            data_clean[col] = data_clean[col].fillna(data_clean[col].mean())

    for col in ["horsepower", "price", "normalized-losses"]:
        if col in data_clean.columns and data_clean[col].isnull().sum() > 0:
            data_clean[col] = data_clean[col].fillna(data_clean[col].median())

    n_after = len(data_clean)
    missing_after = data_clean.isnull().sum().sum()

    print("\n===== Ringkasan Data Cleaning =====")
    print(f"Jumlah data sebelum cleaning : {n_before}")
    print(f"Jumlah data sesudah cleaning : {n_after}")
    print(f"Jumlah baris duplikat yang dihapus: {n_dupe}")
    print(f"Total missing values sebelum : {missing_before}")
    print(f"Total missing values sesudah : {missing_after}")

    return data_clean


# Transofrmation
def transform_data(data: pd.DataFrame) -> pd.DataFrame:
    data_transformed = data.copy()
    _, numerical_column = get_column_types(data_transformed)

    print("\n===== Ringkasan Data Transformation =====")

    # Normalisasi kolom numerik dengan Min-Max Scaling
    if numerical_column:
        before_sample = data_transformed[numerical_column].head(3).copy()
        scaler = MinMaxScaler()
        data_transformed[numerical_column] = scaler.fit_transform(data_transformed[numerical_column])
        print(f"Normalisasi (Min-Max Scaling) diterapkan pada: {numerical_column}")
        print("Contoh sebelum:\n", before_sample)
        print("Contoh sesudah:\n", data_transformed[numerical_column].head(3))

    # One-hot encoding
    if all(col in data_transformed.columns for col in ONE_HOT_COLS):
        data_transformed = pd.get_dummies(data_transformed, columns=ONE_HOT_COLS)
        print(f"One-hot encoding diterapkan pada: {ONE_HOT_COLS}")

    # Frequency encoding
    for col in FREQUENCY_ENCODING_COLS:
        if col in data_transformed.columns:
            freq = data_transformed[col].value_counts(normalize=True)
            data_transformed[col] = data_transformed[col].map(freq)
    print(f"Frequency encoding diterapkan pada: {FREQUENCY_ENCODING_COLS}")

    # Label encoding
    le = LabelEncoder()
    for col in LABEL_ENCODING_COLS:
        if col in data_transformed.columns:
            data_transformed[col] = le.fit_transform(data_transformed[col].astype(str))
    print(f"Label encoding diterapkan pada: {LABEL_ENCODING_COLS}")

    return data_transformed


# Export dataset
def save_data(data: pd.DataFrame, filepath: Path) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(filepath, index=False)
    print(f"\nProcessed dataset disimpan di: {filepath}")


# Pipeline
def run_pipeline(raw_path: Path = RAW_PATH, processed_path: Path = PROCESSED_PATH) -> pd.DataFrame:
    # Extract
    data_raw = load_data(raw_path)
    inspect_data(data_raw, label="Raw Dataset")

    # Transform
    data_clean = clean_data(data_raw)
    data_transformed = transform_data(data_clean)

    # Load
    save_data(data_transformed, processed_path)

    return data_transformed


if __name__ == "__main__":
    run_pipeline()

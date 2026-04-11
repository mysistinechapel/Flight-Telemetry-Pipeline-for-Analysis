import pandas as pd
from pathlib import Path

RAW_PARQUET_DATA_PATH = Path("data/raw/parquet/")
PROCESSED_PARQUET_DATA_PATH = Path("data/processed/parquet/")
DATE_COLS = ["DATE_YEAR", "DATE_MONTH", "DATE_DAY", "GMT_HOUR", "GMT_MINUTE", "GMT_SEC"]


def load_flight(parquet_file_path):
    return pd.read_parquet(parquet_file_path)

def build_timestamp(df):
    for col in DATE_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["timestamp"] = pd.to_datetime({
        "year": df["DATE_YEAR"],
        "month": df["DATE_MONTH"],
        "day": df["DATE_DAY"],
        "hour": df["GMT_HOUR"],
        "minute": df["GMT_MINUTE"],
        "second": df["GMT_SEC"],
    }, errors="coerce")
    return df

def normalize_data(df):
    df.columns = df.columns.str.strip()
    return df

def sort_and_clean(df):
    df = df.sort_values(by=["timestamp"]).reset_index(drop=True)
    return df

def main():

    processed = 0
    skipped = 0
    failed = 0

    # Confirm the raw parquet data path exists
    if not RAW_PARQUET_DATA_PATH.exists():
        raise FileNotFoundError(f"{RAW_PARQUET_DATA_PATH} does not exist")

    # Creates parquet data path if doesn't exist. If it exists, we do nothing.
    PROCESSED_PARQUET_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    for parquet_file_name in RAW_PARQUET_DATA_PATH.glob("*.parquet"):
        try:
            print(f"Processing {parquet_file_name.name}")

            # Build Parquet processed output path
            parquet_processed_file_name = PROCESSED_PARQUET_DATA_PATH / parquet_file_name.name

            if parquet_processed_file_name.exists():
                print(f"Skipping: {parquet_file_name.name}")
                skipped += 1
                continue

            df = load_flight(parquet_file_name)
            df = normalize_data(df)
            df = build_timestamp(df)
            df = sort_and_clean(df)

            df.to_parquet(parquet_processed_file_name)
            processed += 1

        except Exception as e:
            failed += 1
            print(f"Exception while processing {parquet_file_name.name}: {e}")

    # Outputs summary counts of processed and failed files
    print("SUMMARY RESULTS")
    print(f"Processed: {processed}")
    print(f"Skipped: {skipped}")
    print(f"Failed: {failed}")
if __name__ == "__main__":
    main()
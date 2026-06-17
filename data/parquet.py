import pandas as pd

df = pd.read_excel(
    "dehradun_master_dataset_cleaned.xlsx"
)

df.to_parquet(
    "dehradun_master_dataset.parquet",
    index=False
)

print("✅ Parquet file created successfully")
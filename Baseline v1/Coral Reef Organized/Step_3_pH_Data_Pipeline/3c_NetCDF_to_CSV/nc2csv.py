import xarray as xr
import pandas as pd
import os
import numpy as np

# Load dataset
dataset_path = 'D:/AI Project LAT/monthly_global_ph.nc'  # Update to your file path
output_folder = 'D:/AI Project LAT/monthly_csvs/'  # Folder to save monthly CSVs
os.makedirs(output_folder, exist_ok=True)

print("Loading dataset...")
ds = xr.open_dataset(dataset_path)

# Convert to DataFrame
print("Converting dataset to DataFrame...")
df = ds.to_dataframe().reset_index()

# Reduce memory usage
print("Optimizing memory usage...")
df['latitude'] = df['latitude'].astype('float32')
df['longitude'] = df['longitude'].astype('float32')
df['ph'] = df['ph'].astype('float32')

# Filter by time range
print("Filtering data for the specified time range...")
filtered_df = df[(df['time'] >= '2006-10-01') & (df['time'] <= '2022-10-31')]

# Check filtered DataFrame shape
print(f"Filtered data shape: {filtered_df.shape}")

# Group data by month
print("Grouping data by month...")
filtered_df['time'] = pd.to_datetime(filtered_df['time'])
grouped = filtered_df.groupby(filtered_df['time'].dt.to_period('M'))

# Save each group as a separate CSV
print("Saving monthly data to CSV files...")
for period, group in grouped:
    year_month = str(period)
    output_path = os.path.join(output_folder, f"{year_month}.csv")
    print(f"Saving {year_month} to {output_path}...")
    group.to_csv(output_path, index=False)

print("All monthly CSVs saved successfully!")

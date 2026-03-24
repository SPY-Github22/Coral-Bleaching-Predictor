import xarray as xr
import numpy as np
import pandas as pd
from tqdm import tqdm

# Paths to the datasets
yearly_dataset_path = r"D:\AI Project LAT\GLOBAL_OMI_HEALTH_carbon_ph_area_averaged_subset.nc"
trend_dataset_path = r"D:\AI Project LAT\GLOBAL_OMI_HEALTH_carbon_ph_trend_subset.nc"
output_combined_path = r"D:\AI Project LAT\monthly_global_ph.nc"

# Load datasets
print("Loading yearly dataset...")
yearly_ds = xr.open_dataset(yearly_dataset_path)
print("Loading trend dataset...")
trend_ds = xr.open_dataset(trend_dataset_path)

# Extract relevant data
yearly_time = yearly_ds['time']
yearly_ph = yearly_ds['ph']
ph_trend = trend_ds['ph_trend']

# Generate monthly timestamps
monthly_time = pd.date_range(start=str(yearly_time[0].values), end=str(yearly_time[-1].values), freq='ME')

# Convert time to integers (timestamps in nanoseconds) for interpolation
yearly_time_int = yearly_time.astype('datetime64[ns]').astype(np.int64)
monthly_time_int = monthly_time.astype('datetime64[ns]').astype(np.int64)

# Interpolate pH to monthly resolution
print("Interpolating yearly pH data to monthly resolution...")
interpolated_ph = np.interp(
    monthly_time_int,
    yearly_time_int,
    yearly_ph
)

# Create an empty array to store the monthly global pH values
print("Calculating global pH per month...")
monthly_global_ph = np.zeros((len(monthly_time), len(ph_trend.latitude), len(ph_trend.longitude)))

for i, month in enumerate(tqdm(monthly_time, desc="Processing months")):
    # Apply spatial trend
    monthly_global_ph[i, :, :] = interpolated_ph[i] + ph_trend

# Create a new xarray dataset for the combined data
print("Creating new dataset...")
monthly_ds = xr.Dataset(
    {
        "ph": (["time", "latitude", "longitude"], monthly_global_ph),
    },
    coords={
        "time": monthly_time,
        "latitude": ph_trend.latitude,
        "longitude": ph_trend.longitude,
    },
    attrs={
        "title": "Monthly Global pH Derived from Interpolated Yearly Data and Trends",
        "source": "E.U. Copernicus Marine Service Information",
    }
)

# Save to NetCDF
print(f"Saving combined dataset to {output_combined_path}...")
monthly_ds.to_netcdf(output_combined_path)
print(f"Dataset saved successfully: {output_combined_path}")

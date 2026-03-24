import xarray as xr

# File paths
trend_file = r'D:\AI Project LAT\global_omi_health_carbon_ph_trend_1985_P20230930.nc'
monthly_file = r'D:\AI Project LAT\GLOBAL_OMI_HEALTH_carbon_ph_area_averaged_subset.nc'  # Replace with the subsetted monthly dataset
output_file = r'D:\AI Project LAT\combined_pH_and_trend_subset.nc'

# Load the trend dataset
print("Loading trend dataset...")
trend_ds = xr.open_dataset(trend_file)

# Inspect the trend dataset
print(trend_ds)

# Subset the trend dataset (if it has a time dimension)
# Replace 'time' with the actual time dimension name in the dataset, if it exists
if 'time' in trend_ds.dims:
    print("Subsetting trend dataset...")
    time_range = slice('2006-10-01', '2022-10-31')
    trend_ds = trend_ds.sel(time=time_range)

# Save the subsetted trend dataset (optional)
trend_subset_file = r'D:\AI Project LAT\GLOBAL_OMI_HEALTH_carbon_ph_trend_subset.nc'
trend_ds.to_netcdf(trend_subset_file)
print(f"Subsetted trend dataset saved to {trend_subset_file}")

# Load the monthly pH dataset (subsetted)
print("Loading monthly pH dataset...")
monthly_ds = xr.open_dataset(monthly_file)

# Combine datasets
# Assuming both datasets have matching spatial dimensions (lat/lon)
print("Combining datasets...")
combined_ds = monthly_ds.copy()
combined_ds['ph_trend'] = trend_ds['ph_trend']  # Replace 'ph_trend' with the actual variable name in the trend dataset

# Save the combined dataset to a new NetCDF file
combined_ds.to_netcdf(output_file)

print(f"Combined dataset saved to {output_file}")
print(combined_ds)

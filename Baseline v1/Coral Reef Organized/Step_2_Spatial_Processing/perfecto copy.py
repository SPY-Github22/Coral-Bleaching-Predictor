import geopandas as gpd
import pandas as pd

# File Paths
reef_extent_path = 'reefextent.gpkg'
benthic_path = 'benthic.gpkg'
boundary_path = 'boundary.geojson'
statistics_path = 'statistics.csv'

# --- Step 1: Load the Spatial Data ---
reef_extent = gpd.read_file(reef_extent_path)
benthic = gpd.read_file(benthic_path)
boundary = gpd.read_file(boundary_path)

# Ensure consistent CRS
reef_extent = reef_extent.to_crs(boundary.crs)
benthic = benthic.to_crs(boundary.crs)

# Visualize (optional)
print("Reef Extent CRS:", reef_extent.crs)
print("Benthic Zones CRS:", benthic.crs)
print("Boundary CRS:", boundary.crs)

# --- Step 2: Combine Spatial Data ---
# Perform a spatial join
combined_data = gpd.sjoin(reef_extent, benthic, how='inner', predicate='intersects')

# Clip to the boundary
clipped_data = gpd.clip(combined_data, boundary)

# --- Step 3: Add Features ---
# Calculate reef area
# Ensure proper CRS for area calculations
clipped_data = clipped_data.to_crs(epsg=3395)  # World Mercator (meters)

# Calculate reef area in square meters

clipped_data['reef_area'] = clipped_data.geometry.area
print("Columns in clipped_data:", clipped_data.columns)
# Add reef type indicator (example: identifying coral zones)
#clipped_data['is_coral'] = clipped_data['class_type'].apply(lambda x: 1 if 'Coral' in x else 0)

# Fix the coral zone indicator
if 'class_type' in clipped_data.columns:
    clipped_data['is_coral'] = clipped_data['class_type'].apply(lambda x: 1 if 'Coral' in x else 0)
else:
    # Use an alternative column or skip this step if no suitable column exists
    print("Column 'class_type' not found in clipped_data. Skipping 'is_coral' feature.")
    clipped_data['is_coral'] = 0  # Placeholder, adjust as needed

# --- Step 4: Merge with Tabular Data ---
# Load tabular data
statistics = pd.read_csv(statistics_path)

# Inspect available columns in both datasets
print("Columns in clipped_data:", clipped_data.columns)
print("Columns in statistics:", statistics.columns)

# Determine the correct column to use for merging
# Replace 'class_left' and 'class_right' with the appropriate column if needed
if 'class_left' in clipped_data.columns and 'class_name' in statistics.columns:
    merged_data = clipped_data.merge(statistics, left_on='class_left', right_on='class_name', how='left')
elif 'class_right' in clipped_data.columns and 'class_name' in statistics.columns:
    merged_data = clipped_data.merge(statistics, left_on='class_right', right_on='class_name', how='left')
else:
    print("No matching key found for merging clipped_data and statistics. Exiting.")
    merged_data = None

if merged_data is not None:
    # Inspect merged data
    print("Merged Data Columns:", merged_data.columns)
    # Handle missing values if any
    merged_data = merged_data.dropna()
    # Save processed spatial data
    merged_data.to_file('processed_spatial_data.gpkg', driver='GPKG')

# Merge based on a common column (adjust column names if needed)
#merged_data = clipped_data.merge(statistics, left_on='class_name', right_on='class_name', how='left')



# Save processed spatial data for later use
#merged_data.to_file('processed_spatial_data.gpkg', driver='GPKG')

# --- Optional: Visualize the Merged Data ---
import matplotlib.pyplot as plt

merged_data.plot(column='reef_area', legend=True, cmap='YlGnBu')
plt.title("Reef Area in Coral Zones")
plt.savefig("reef_area_map.png")
plt.show()

import geopandas as gpd
import plotly.express as px

# --- Step 1: Load the Processed Spatial Data ---
print("Loading processed spatial data...")
processed_spatial_data_path = 'processed_spatial_data.gpkg'
merged_data = gpd.read_file(processed_spatial_data_path)
print("Spatial data loaded successfully!")

# Reproject to WGS84 for compatibility with Plotly
print("Converting CRS to WGS84 for visualization...")
merged_data = merged_data.to_crs(epsg=4326)
print("CRS conversion completed!")

# Simplify geometries for better performance
print("Simplifying geometries for performance...")
merged_data["simplified_geometry"] = merged_data.geometry.simplify(tolerance=0.01, preserve_topology=True) #Increase tolerance = Low Power Enough
print("Geometry simplification completed!")

# Calculate centroids in projected CRS for accuracy
print("Reprojecting to a projected CRS for accurate centroid calculation...")
projected_data = merged_data.to_crs(epsg=3395)  # World Mercator (meters)
projected_data["centroid"] = projected_data.geometry.centroid
print("Centroids calculated in projected CRS!")

# Convert centroids back to WGS84 for map display
print("Converting centroids back to WGS84...")
merged_data["centroid"] = projected_data["centroid"].to_crs(epsg=4326)
merged_data["latitude"] = merged_data["centroid"].y
merged_data["longitude"] = merged_data["centroid"].x
print("Centroids converted to WGS84!")

# Format `reef_area` values for readability
print("Formatting reef area values for hover tooltips...")
merged_data["reef_area_formatted"] = merged_data["reef_area"].apply(lambda x: f"{x:,.0f} sq meters")
print("Reef area formatting completed!")

# --- Step 2: Create an Interactive Map ---
print("Creating interactive map with dynamic color scale...")
fig = px.choropleth_mapbox(
    merged_data,
    geojson=merged_data["simplified_geometry"],
    locations=merged_data.index,
    color="reef_area",
    color_continuous_scale="Viridis",
    range_color=None,  # Allow Plotly to automatically adjust the color scale dynamically
    hover_data={
        "reef_area_formatted": True,  # Show formatted reef area
        "latitude": True,             # Show latitude
        "longitude": True,            # Show longitude
        "reef_area": False,           # Hide raw reef area
    },
    mapbox_style="open-street-map",
    center={"lat": merged_data["latitude"].mean(), "lon": merged_data["longitude"].mean()},
    zoom=6,
    opacity=0.7,
    title="Interactive Reef Area Map"
)

# --- Save the Map ---
print("Saving interactive map as an HTML file...")
fig.write_html("interactive_reef_area_map.html")
print("Map saved as 'interactive_reef_area_map.html'. Open it in a browser for persistent access.")

# --- Display the Map ---
print("Displaying the map...")
fig.show()
print("Map displayed successfully!")

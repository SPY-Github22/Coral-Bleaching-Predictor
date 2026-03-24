import geopandas as gpd
import plotly.express as px
import os
import webbrowser

def generate_and_open_map(data_path='processed_spatial_data.gpkg', output_path='interactive_reef_area_map.html'):
    """
    Generates an interactive map of reef areas and opens it instantly in the default browser.
    
    Parameters:
        data_path (str): Path to the processed spatial data file.
        output_path (str): Path to save the interactive map HTML file.
    """
    # Check if the map already exists
    if os.path.exists(output_path):
        print(f"Map already exists at {output_path}. Opening it directly...")
        webbrowser.open(f"file://{os.path.abspath(output_path)}")
        return

    print("Loading processed spatial data...")
    merged_data = gpd.read_file(data_path)
    print("Spatial data loaded successfully!")

    print("Converting CRS to WGS84 for visualization...")
    merged_data = merged_data.to_crs(epsg=4326)
    print("CRS conversion completed!")

    print("Simplifying geometries for performance...")
    merged_data["simplified_geometry"] = merged_data.geometry.simplify(tolerance=0.01, preserve_topology=True)
    print("Geometry simplification completed!")

    print("Reprojecting to a projected CRS for accurate centroid calculation...")
    projected_data = merged_data.to_crs(epsg=3395)
    projected_data["centroid"] = projected_data.geometry.centroid
    print("Centroids calculated in projected CRS!")

    print("Converting centroids back to WGS84...")
    merged_data["centroid"] = projected_data["centroid"].to_crs(epsg=4326)
    merged_data["latitude"] = merged_data["centroid"].y
    merged_data["longitude"] = merged_data["centroid"].x
    print("Centroids converted to WGS84!")

    print("Formatting reef area values for hover tooltips...")
    merged_data["reef_area_formatted"] = merged_data["reef_area"].apply(lambda x: f"{x:,.0f} sq meters")
    print("Reef area formatting completed!")

    print("Creating interactive map...")
    fig = px.choropleth_mapbox(
        merged_data,
        geojson=merged_data["simplified_geometry"],
        locations=merged_data.index,
        color="reef_area",
        color_continuous_scale="Viridis",
        hover_data={
            "reef_area_formatted": True,
            "latitude": True,
            "longitude": True,
        },
        mapbox_style="open-street-map",
        center={"lat": merged_data["latitude"].mean(), "lon": merged_data["longitude"].mean()},
        zoom=6,
        opacity=0.7,
        title="Interactive Reef Area Map"
    )

    print(f"Saving map to {output_path}...")
    fig.write_html(output_path)
    print(f"Map saved successfully! Opening {output_path} in the browser...")

    # Open the saved map in the default browser
    webbrowser.open(f"file://{os.path.abspath(output_path)}")

# Example usage
generate_and_open_map()

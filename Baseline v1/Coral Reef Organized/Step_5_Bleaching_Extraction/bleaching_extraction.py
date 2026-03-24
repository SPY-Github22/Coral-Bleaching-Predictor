import os
import pandas as pd
import numpy as np
from PIL import Image
from sklearn.neighbors import KDTree
from concurrent.futures import ProcessPoolExecutor
import pickle

# --- Constants ---
BLEACHING_LEVELS = {
    "No Stress": (173, 216, 230),  # Light Blue
    "Watch": (255, 255, 0),       # Yellow
    "Warning": (255, 165, 0),     # Orange
    "Alert Level 1": (255, 0, 0), # Red
    "Alert Level 2": (165, 42, 42), # Brown
    "Alert Level 3": (255, 20, 147), # Dark Pink
    "Alert Level 4": (128, 0, 128), # Purple
    "Alert Level 5": (153, 50, 204)  # Bright Purple
}
TOLERANCE = 10  # RGB tolerance for color matching

# --- Functions ---
def log_unmatched_pixel(pixel):
    """Log unmatched pixel colors."""
    with open("unmatched_colors.log", "a") as log_file:
        log_file.write(f"Unmatched pixel color: {pixel}\n")

def count_alert_levels(data):
    """Count occurrences of each alert level."""
    counts = data['Alert Level'].value_counts()
    print("Alert Level Counts:")
    print(counts)

def get_nearest_alert(lat, lon, data, kdtree):
    """Find the nearest alert level based on latitude and longitude."""
    dist, idx = kdtree.query([[lat, lon]], k=1)
    return data.iloc[idx[0][0]]['Alert Level'] if dist[0][0] <= 0.5 else "No Stress"

def process_image_section(y_start, y_end, pixels, h, w, neighbors_data, neighbors_tree):
    """Process a section of the image and return bleaching data."""
    section_data = []
    unmatched_count = 0

    for y in range(y_start, y_end):
        for x in range(w):
            r, g, b = pixels[y, x]

            # Match pixel color to bleaching level
            matched_level = None
            for level, color in BLEACHING_LEVELS.items():
                if all(abs(c1 - c2) <= TOLERANCE for c1, c2 in zip((r, g, b), color)):
                    matched_level = level
                    break

            if matched_level is None:
                # Log unmatched colors
                log_unmatched_pixel((r, g, b))
                unmatched_count += 1

                # Use neighbors if no exact match
                lat = 90 - (y / h) * 180
                lon = -180 + (x / w) * 360
                if neighbors_data is not None:
                    matched_level = get_nearest_alert(lat, lon, neighbors_data, neighbors_tree)
                else:
                    matched_level = "No Stress"

            # Compute latitude and longitude
            lat = 90 - (y / h) * 180
            lon = -180 + (x / w) * 360

            section_data.append((lat, lon, matched_level))

    return section_data, unmatched_count

def extract_bleaching_data(args):
    """Extract bleaching data from an image and save it to a CSV."""
    image_path, output_csv, neighbors_csv = args
    print(f"Processing {image_path}...")
    image = Image.open(image_path)
    image = image.convert('RGB')
    pixels = np.array(image)
    h, w, _ = pixels.shape

    # If neighbors CSV is provided, load and prepare KDTree
    if neighbors_csv and os.path.exists(neighbors_csv):
        neighbors_data = pd.read_csv(neighbors_csv)
        neighbors_tree = KDTree(neighbors_data[["Latitude", "Longitude"].values])
    else:
        neighbors_data = None
        neighbors_tree = None

    # Split image into sections for parallel processing
    num_sections = os.cpu_count() or 4
    section_height = h // num_sections
    sections = [(i * section_height, (i + 1) * section_height if i < num_sections - 1 else h)
                for i in range(num_sections)]

    # Process sections in parallel
    bleaching_data = []
    unmatched_count = 0
    with ProcessPoolExecutor() as executor:
        results = executor.map(
            process_image_section_with_pickle,
            [(s[0], s[1], pixels, h, w, neighbors_data, neighbors_tree) for s in sections]
        )
        for section_data, section_unmatched in results:
            bleaching_data.extend(section_data)
            unmatched_count += section_unmatched

    # Save data to CSV
    df = pd.DataFrame(bleaching_data, columns=["Latitude", "Longitude", "Alert Level"])
    df.to_csv(output_csv, index=False)
    print(f"Saved extracted data to {output_csv}")

    # Log summary
    print(f"Unmatched pixels: {unmatched_count}")
    count_alert_levels(df)

def process_image_section_with_pickle(args):
    """Wrapper for pickle compatibility."""
    return process_image_section(*args)

# --- Main Execution ---
def main():
    input_dir = "coral_bleaching_images"  # Directory containing bleaching images
    output_dir = "bleaching_csv"    # Directory to save CSV files
    neighbors_csv = "combined_neighbors.csv"  # CSV containing neighbor data

    os.makedirs(output_dir, exist_ok=True)

    tasks = []
    for filename in os.listdir(input_dir):
        if filename.endswith(".png"):
            image_path = os.path.join(input_dir, filename)
            output_csv = os.path.join(output_dir, filename.replace(".png", ".csv"))
            tasks.append((image_path, output_csv, neighbors_csv))

    with ProcessPoolExecutor() as executor:
        executor.map(extract_bleaching_data, tasks)

if __name__ == "__main__":
    main()

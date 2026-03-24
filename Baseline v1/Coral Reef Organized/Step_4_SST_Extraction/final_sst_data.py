import cv2
import numpy as np
import csv
import os
from scipy.spatial import KDTree

# Directory containing SST images
sst_images_dir = 'sst_images'  # Path to your directory with images
output_dir = 'output_csv'  # Directory to save the CSV files

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Define temperature-to-RGB mappings (from the color scale extraction)
temp_to_rgb = {
    -2: (17, 24, 88), -1: (18, 27, 96), 0: (20, 31, 101), 1: (23, 36, 106),
    2: (29, 41, 112), 3: (35, 45, 117), 4: (42, 49, 122), 5: (50, 54, 128),
    6: (56, 58, 132), 7: (64, 63, 137), 8: (73, 67, 139), 9: (83, 71, 141),
    10: (91, 74, 142), 11: (102, 79, 143), 12: (111, 82, 146), 13: (119, 86, 148),
    14: (129, 90, 148), 15: (137, 94, 150), 16: (147, 97, 152), 17: (155, 101, 152),
    18: (160, 104, 150), 19: (165, 108, 148), 20: (171, 112, 146), 21: (176, 116, 145),
    22: (181, 119, 142), 23: (187, 122, 140), 24: (194, 126, 138), 25: (198, 129, 135),
    26: (203, 134, 136), 27: (209, 145, 142), 28: (214, 157, 149), 29: (219, 168, 157),
    30: (225, 180, 166), 31: (231, 191, 173), 32: (236, 202, 181), 33: (240, 214, 189),
    34: (246, 226, 196), 35: (249, 236, 208)
}

# Build a KDTree for nearest neighbor search
rgb_values = np.array(list(temp_to_rgb.values()))
temp_values = list(temp_to_rgb.keys())
rgb_tree = KDTree(rgb_values)

# Function to determine if a pixel is land (gray regions)
def is_land(pixel):
    return 100 <= pixel[0] <= 160 and 100 <= pixel[1] <= 160 and 100 <= pixel[2] <= 160

# Process each image in the directory
for filename in os.listdir(sst_images_dir):
    if filename.endswith('.png') or filename.endswith('.jpg'):  # Adjust extensions as needed
        map_image_path = os.path.join(sst_images_dir, filename)
        map_image = cv2.imread(map_image_path)

        if map_image is None:
            print(f"Error: Could not load the map image from {map_image_path}. Skipping...")
            continue

        print(f"Processing {filename}...")

        # Dimensions of the map image
        image_height, image_width, _ = map_image.shape

        # Output CSV file
        csv_file_path = os.path.join(output_dir, f'{os.path.splitext(filename)[0]}.csv')

        # Open the CSV file for writing
        with open(csv_file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Latitude", "Longitude", "Temperature (°C)"])

            for y in range(image_height):
                for x in range(image_width):
                    # Get the pixel's RGB value (convert BGR to RGB)
                    pixel = map_image[y, x][::-1]

                    # Skip land areas
                    if is_land(pixel):
                        continue

                    # Find the nearest RGB value in the temperature scale
                    dist, idx = rgb_tree.query(pixel)
                    temperature = temp_values[idx]

                    # Convert pixel coordinates to latitude and longitude
                    latitude = 90 - (y / image_height) * 180
                    longitude = (x / image_width) * 360 - 180

                    # Write the data to the CSV file
                    writer.writerow([latitude, longitude, temperature])

        print(f"Temperature data saved to {csv_file_path}.")

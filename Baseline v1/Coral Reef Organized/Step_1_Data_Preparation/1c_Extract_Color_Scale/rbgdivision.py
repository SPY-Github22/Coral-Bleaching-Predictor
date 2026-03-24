import cv2
import numpy as np

# Load the color scale image directly
image_path = 'sst_images/colour scale.png'
image_color_scale = cv2.imread(image_path)

if image_color_scale is None:
    print(f"Error: Could not load the color scale image from {image_path}.")
    exit(1)
else:
    print("Color scale image loaded successfully.")

# Print image dimensions
image_height, image_width, _ = image_color_scale.shape
print(f"Image dimensions: Height={image_height}, Width={image_width}")

# Define the temperature values
temperatures = list(range(-2, 36))  # Temperatures from -2 to 35

# Calculate the exact width of each temperature section
bar_width = image_color_scale.shape[1]
section_width = bar_width / len(temperatures)  # Floating-point division for precision

rgb_ranges = {}

# Interpolate between the known color points
start_color = np.array([14, 24, 93])  # Approx. RGB for #0E185D
mid_color = np.array([158, 103, 156])  # Approx. RGB for #9E679C
end_color = np.array([255, 240, 202])  # Approx. RGB for #FFF0CA

def interpolate_color(temp):
    if temp <= 16.5:
        factor = (temp - (-2)) / (16.5 - (-2))
        return (1 - factor) * start_color + factor * mid_color
    else:
        factor = (temp - 16.5) / (35 - 16.5)
        return (1 - factor) * mid_color + factor * end_color

# Extract RGB values for each temperature
for i, temp in enumerate(temperatures):
    section_start = int(round(i * section_width))
    section_end = int(round((i + 1) * section_width)) if i < len(temperatures) - 1 else bar_width

    section = image_color_scale[:, section_start:section_end]

    # Flatten all pixels in the section
    pixels = section.reshape(-1, 3)  # Reshape to (num_pixels, 3)

    # Filter out near-white pixels with adaptive thresholding
    valid_pixels = [tuple(pixel[::-1]) for pixel in pixels if not np.all(pixel >= 240)]  # BGR to RGB

    # Average the RGB values from the valid pixels
    if valid_pixels:
        avg_color = tuple(np.mean(valid_pixels, axis=0).astype(int))
        rgb_ranges[temp] = avg_color
    else:
        # Use interpolation if no valid colors found
        interpolated_color = interpolate_color(temp).astype(int)
        rgb_ranges[temp] = tuple(interpolated_color)

    # Debugging output
    print(f"Temperature {temp}°C: Average RGB = {rgb_ranges.get(temp, 'Interpolated color')}")

# Output the RGB ranges
print("\nExtracted RGB ranges for the temperature scale:")
for temp, rgb in rgb_ranges.items():
    print(f"{temp}°C: {rgb}")

# Optional: Visualize the extracted RGB ranges (e.g., as a bar plot)
try:
    import matplotlib.pyplot as plt

    temps = list(rgb_ranges.keys())
    colors = [tuple(v / 255.0 for v in rgb_ranges[t]) for t in temps]

    plt.figure(figsize=(12, 2))
    for i, color in enumerate(colors):
        plt.fill_between([i, i + 1], 0, 1, color=color)

    plt.xticks(range(len(temps)), temps, rotation=90)
    plt.title("Extracted Temperature Colors")
    plt.show()
except ImportError:
    print("Matplotlib not installed. Skipping visualization.")

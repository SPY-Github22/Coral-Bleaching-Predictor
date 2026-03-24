import os
import pandas as pd
from scipy.spatial import cKDTree

# --- Input and Output Directories ---
bleaching_folder = "bleaching_csv"
ph_folder = "full_clean"
sst_folder = "output_csv"
output_folder = "final_out"
os.makedirs(output_folder, exist_ok=True)

# --- Tolerance for Latitude/Longitude Matching ---
TOLERANCE = 0.1  # Increased tolerance for better matching

# --- Helper Function to Load and Index Data ---
def load_data(file_path, columns, lat_col="Latitude", lon_col="Longitude", sst_mode=False):
    """Load CSV and build a KDTree for spatial matching."""
    try:
        # Attempt to read the CSV with fallback encoding
        data = pd.read_csv(file_path, encoding='utf-8')
        print(f"Loaded {len(data)} rows from {file_path}")

        if sst_mode:
            # Special handling for SST data (assume third column as Temperature(C))
            data.columns = ["Latitude", "Longitude", "Temperature(C)"]
        else:
            # Validate columns
            missing_columns = [col for col in columns if col not in data.columns]
            if missing_columns:
                print(f"Missing columns {missing_columns} in {file_path}")
                return pd.DataFrame(), None

        data = data[columns].dropna()
        print(f"Filtered to {len(data)} valid rows based on columns {columns}")
        tree = cKDTree(data[[lat_col, lon_col]].values)
        return data, tree
    except UnicodeDecodeError:
        print(f"Retrying with 'latin1' encoding for {file_path}")
        try:
            data = pd.read_csv(file_path, encoding='latin1')
            print(f"Loaded {len(data)} rows from {file_path} (latin1 encoding)")

            if sst_mode:
                # Special handling for SST data (assume third column as Temperature(C))
                data.columns = ["Latitude", "Longitude", "Temperature(C)"]
            else:
                # Validate columns
                missing_columns = [col for col in columns if col not in data.columns]
                if missing_columns:
                    print(f"Missing columns {missing_columns} in {file_path}")
                    return pd.DataFrame(), None

            data = data[columns].dropna()
            print(f"Filtered to {len(data)} valid rows based on columns {columns}")
            tree = cKDTree(data[[lat_col, lon_col]].values)
            return data, tree
        except Exception as e:
            print(f"Failed to load {file_path} with latin1 encoding: {e}")
            return pd.DataFrame(), None
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return pd.DataFrame(), None

# --- Function to Match Rows Across Datasets ---
def match_and_merge(sst_file, ph_file, bleaching_file):
    """Merge SST, pH, and bleaching data for a given month-year."""
    try:
        # Load data
        sst_data, sst_tree = load_data(sst_file, ["Latitude", "Longitude", "Temperature(C)"], sst_mode=True)
        ph_data, ph_tree = load_data(ph_file, ["latitude", "longitude", "ph"], "latitude", "longitude")
        bleaching_data, bleaching_tree = load_data(bleaching_file, ["Latitude", "Longitude", "Alert Level"])

        if sst_tree is None or ph_tree is None or bleaching_tree is None:
            print("Skipping due to missing data trees.")
            return None

        # Prepare output data
        combined_data = []

        for _, sst_row in sst_data.iterrows():
            sst_lat, sst_lon, temp = sst_row

            # Match with pH data
            dist, ph_idx = ph_tree.query([sst_lat, sst_lon], distance_upper_bound=TOLERANCE)
            ph = None
            if dist != float("inf"):
                ph_row = ph_data.iloc[ph_idx]
                ph = ph_row["ph"]

            # Match with bleaching data
            dist, bleaching_idx = bleaching_tree.query([sst_lat, sst_lon], distance_upper_bound=TOLERANCE)
            alert_level = None
            if dist != float("inf"):
                bleaching_row = bleaching_data.iloc[bleaching_idx]
                alert_level = bleaching_row["Alert Level"]

            # Append merged row only if all three datasets contribute
            if temp is not None and ph is not None and alert_level is not None:
                combined_data.append((sst_lat, sst_lon, temp, ph, alert_level))

        # Debugging: Log combined rows
        if combined_data:
            print(f"Matched {len(combined_data)} rows for {sst_file}")
        else:
            print(f"No matches found for {sst_file}")

        # Return combined DataFrame
        return pd.DataFrame(combined_data, columns=["Latitude", "Longitude", "Temperature(C)", "pH", "Alert Level"])
    except Exception as e:
        print(f"Error processing files: {sst_file}, {ph_file}, {bleaching_file}: {e}")
        return None

# --- Main Processing Loop ---
# Create mapping for month formats
def normalize_month_format(file_name, source_format="bleaching"):
    if source_format == "bleaching":
        # Example: april_2007 -> 2007-04
        month, year = file_name.split("_")
        month_number = {
            "january": "01", "february": "02", "march": "03", "april": "04", "may": "05", "june": "06",
            "july": "07", "august": "08", "september": "09", "october": "10", "november": "11", "december": "12"
        }.get(month.lower(), None)
        return f"{year}-{month_number}" if month_number else None
    elif source_format == "ph":
        # Example: 2007-04 -> april_2007
        year, month = file_name.split("-")
        month_name = {
            "01": "january", "02": "february", "03": "march", "04": "april", "05": "may", "06": "june",
            "07": "july", "08": "august", "09": "september", "10": "october", "11": "november", "12": "december"
        }.get(month, None)
        return f"{month_name}_{year}" if month_name else None
    return None

bleaching_months = set(os.path.splitext(f)[0] for f in os.listdir(bleaching_folder))
ph_months = set(normalize_month_format(os.path.splitext(f)[0], "ph") for f in os.listdir(ph_folder))
sst_months = set(os.path.splitext(f)[0] for f in os.listdir(sst_folder))

# Match common months across all datasets
all_months = bleaching_months & ph_months & sst_months

# Debugging: Log all matched months
print(f"Matched months for processing: {sorted(all_months)}")

for month_year in sorted(all_months):
    print(f"Processing {month_year}...")

    # File paths
    bleaching_file = os.path.join(bleaching_folder, f"{month_year}.csv")
    ph_file = os.path.join(ph_folder, f"{normalize_month_format(month_year, 'bleaching')}.csv")
    sst_file = os.path.join(sst_folder, f"{month_year}.csv")

    # Merge data
    combined_df = match_and_merge(sst_file, ph_file, bleaching_file)

    if combined_df is not None and not combined_df.empty:
        output_path = os.path.join(output_folder, f"{month_year}.csv")
        combined_df.to_csv(output_path, index=False)
        print(f"Saved {output_path}")
    else:
        print(f"No valid data for {month_year}, skipping...")

print("Processing complete.")

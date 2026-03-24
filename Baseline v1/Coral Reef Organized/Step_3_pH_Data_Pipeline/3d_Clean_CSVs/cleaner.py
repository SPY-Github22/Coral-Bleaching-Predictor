import pandas as pd
import os

# Folder containing the CSV files
input_folder = 'D:/AI Project LAT/cleaned_monthly_csvs/'
output_folder = 'D:/AI Project LAT/full_clean/'
os.makedirs(output_folder, exist_ok=True)

print("Removing 'time' column from CSV files...")

# Iterate through each file in the folder
for file_name in os.listdir(input_folder):
    if file_name.endswith('.csv'):
        input_path = os.path.join(input_folder, file_name)
        output_path = os.path.join(output_folder, file_name)

        print(f"Processing file: {file_name}")

        # Load the CSV file into a DataFrame
        df = pd.read_csv(input_path)

        # Drop the 'time' column
        if 'time' in df.columns:
            df = df.drop(columns=['time'])

        # Save the updated DataFrame back to a new CSV
        df.to_csv(output_path, index=False)
        print(f"Saved updated file to: {output_path}")

print("All files updated successfully!")

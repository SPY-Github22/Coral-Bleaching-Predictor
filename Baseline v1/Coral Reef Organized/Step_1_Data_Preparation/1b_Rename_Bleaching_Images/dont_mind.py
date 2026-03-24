import os
import calendar

# Function to rename files and add .png extension if not present
def rename_files(folder_path):
    try:
        # List all files in the directory
        files = os.listdir(folder_path)

        for file in files:
            # Extract year and month from the file name
            try:
                if file.startswith("https"):
                    year = file.split("global_")[1][:4]
                    month_num = file.split("global_")[1][4:6]
                    month_name = calendar.month_name[int(month_num)].lower()

                    # Create new file name without the original extension
                    new_name = f"{month_name}_{year}"

                    # Add .png extension to the new name
                    new_name_with_extension = f"{new_name}.png"

                    # Construct full old and new file paths
                    old_file_path = os.path.join(folder_path, file)
                    new_file_path = os.path.join(folder_path, new_name_with_extension)

                    # Rename the file
                    os.rename(old_file_path, new_file_path)
                    print(f"Renamed: {file} -> {new_name_with_extension}")
                else:
                    print(f"Skipped: {file} (does not match pattern)")

            except Exception as e:
                print(f"Error processing file {file}: {e}")

    except Exception as e:
        print(f"Error: {e}")

# Specify the folder path
folder_path = "dont-mind-this"  # Replace with your folder path
rename_files(folder_path)

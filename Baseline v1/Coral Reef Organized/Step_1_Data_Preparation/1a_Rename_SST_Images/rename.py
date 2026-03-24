import os

# Path to the folder containing your PNG files
folder_path = 'sst_images'

# List of month names from October 2006 to October 2022
months = [
    "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october", "november", "december", 
    "january", "february", "march", "april", "may", "june", 
    "july", "august", "september", "october"
]

# Starting frame index for October 2006
frame_index = 51

# Starting year
year = 2006

# Loop through the frames and assign the corresponding month name
for month in months:
    # Construct the new filename: month (e.g., october.png)
    new_filename = f"{month}_{year}.png"
    
    # Construct the old filename: frame_0051.png, frame_0052.png, etc.
    old_filename = f"frame_{frame_index:04d}.png"
    
    # Full old and new file paths
    old_file_path = os.path.join(folder_path, old_filename)
    new_file_path = os.path.join(folder_path, new_filename)
    
    # Rename the file
    os.rename(old_file_path, new_file_path)
    
    # Increment year after December
    if month == "december":
        year += 1
        
    # Print to check
    print(f"Renamed: {old_filename} -> {new_filename}")
    
    # Increment frame index
    frame_index += 1

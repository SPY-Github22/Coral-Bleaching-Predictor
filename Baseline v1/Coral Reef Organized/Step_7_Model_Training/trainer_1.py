import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import numpy as np

# --- Input Directories ---
data_folder = "final_out"
os.makedirs("model", exist_ok=True)

# --- Parameters ---
TOLERANCE = 0.05  # Matching tolerance for lat/lon aggregation

# --- Helper Function: Aggregate Data ---
def aggregate_data(data_folder):
    """Aggregate data into regions with averaged SST and pH, and most prevalent Alert Level."""
    aggregated_data = []

    for file_name in os.listdir(data_folder):
        file_path = os.path.join(data_folder, file_name)
        data = pd.read_csv(file_path)

        # Round latitude and longitude to create approximate regions
        data["Region_Lat"] = (data["Latitude"] // TOLERANCE).astype(int) * TOLERANCE
        data["Region_Lon"] = (data["Longitude"] // TOLERANCE).astype(int) * TOLERANCE

        # Group by region and aggregate
        grouped = data.groupby(["Region_Lat", "Region_Lon"]).agg(
            Avg_Temperature=("Temperature(C)", "mean"),
            Avg_pH=("pH", "mean"),
            Most_Common_Alert_Level=("Alert Level", lambda x: x.mode()[0] if not x.mode().empty else None)
        ).reset_index()

        # Drop rows with missing Alert Level
        grouped = grouped.dropna(subset=["Most_Common_Alert_Level"])
        aggregated_data.append(grouped)

    # Combine all months into a single DataFrame
    return pd.concat(aggregated_data, ignore_index=True)

# --- Load and Aggregate Data ---
print("Aggregating data...")
data = aggregate_data(data_folder)
print(f"Aggregated {len(data)} regions.")

# --- Prepare Features and Labels ---
X = data[["Region_Lat", "Region_Lon", "Avg_Temperature", "Avg_pH"]]
y = data["Most_Common_Alert_Level"]

# Convert categorical target to numeric
alert_level_mapping = {level: idx for idx, level in enumerate(y.unique())}
y = y.map(alert_level_mapping)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# --- Train Random Forest Classifier ---
print("Training model...")
rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, n_jobs=-1, random_state=42)
rf_model.fit(X_train, y_train)

# Save the model
import joblib
model_path = "model/coral_bleaching_predictor.pkl"
joblib.dump((rf_model, alert_level_mapping), model_path)
print(f"Model saved to {model_path}.")

# --- Evaluate Model ---
print("Evaluating model...")
y_pred = rf_model.predict(X_test)
y_test_labels = [list(alert_level_mapping.keys())[list(alert_level_mapping.values()).index(lbl)] for lbl in y_test]
y_pred_labels = [list(alert_level_mapping.keys())[list(alert_level_mapping.values()).index(lbl)] for lbl in y_pred]

print(classification_report(y_test_labels, y_pred_labels))

# --- Instructions for Team Member ---
print("\nInstructions:")
print("1. Use the saved model at 'model/coral_bleaching_predictor.pkl'.")
print("2. Provide latitude and longitude bounds, along with average SST and pH values for the selected region.")
print("3. Use the model to predict the most likely coral bleaching Alert Level for that region.")

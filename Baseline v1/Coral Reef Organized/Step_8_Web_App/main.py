import os
import joblib
import numpy as np
from flask import Flask, render_template, request

# --- Load Trained Model ---
model_path = "model/coral_bleaching_predictor.pkl"
rf_model, alert_level_mapping = joblib.load(model_path)
reverse_mapping = {v: k for k, v in alert_level_mapping.items()}


# --- Define Prediction Function ---
def predict_alert_level(features):
    """Predict the coral bleaching alert level."""
    predicted_label = rf_model.predict([features])[0]
    return reverse_mapping[predicted_label]


# --- Flask App ---
app = Flask(__name__, static_folder="static", template_folder="templates")


# --- Routes ---
@app.route('/')
def home():
    return render_template("frame1.html")


@app.route('/frame2')
def frame2():
    return render_template("frame2.html")


@app.route('/frame3')
def frame3():
    return render_template("frame3.html")


@app.route('/predict_point', methods=['POST'])
def predict_point():
    try:
        lat = float(request.form['lat'])
        lon = float(request.form['lon'])
        avg_sst = float(request.form['sst'])
        avg_ph = float(request.form['ph'])

        # Predict alert level
        alert_level = predict_alert_level([lat, lon, avg_sst, avg_ph])
        return render_template("frame4.html",
                               result=f"Predicted Alert Level: {alert_level}")
    except Exception as e:
        return render_template("frame4.html", result=f"Error: {e}")


@app.route('/predict_area', methods=['POST'])
def predict_area():
    try:
        lat1, lon1 = float(request.form['lat1']), float(request.form['lon1'])
        lat2, lon2 = float(request.form['lat2']), float(request.form['lon2'])
        lat3, lon3 = float(request.form['lat3']), float(request.form['lon3'])
        lat4, lon4 = float(request.form['lat4']), float(request.form['lon4'])
        avg_sst = float(request.form['sst'])
        avg_ph = float(request.form['ph'])

        # Compute region center (approximation)
        region_lat = np.mean([lat1, lat2, lat3, lat4])
        region_lon = np.mean([lon1, lon2, lon3, lon4])

        # Predict alert level
        alert_level = predict_alert_level(
            [region_lat, region_lon, avg_sst, avg_ph])
        return render_template("frame4.html",
                               result=f"Predicted Alert Level: {alert_level}")
    except Exception as e:
        return render_template("frame4.html", result=f"Error: {e}")


# --- Run Flask App ---
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

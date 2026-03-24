import joblib
import numpy as np
from flask import Flask, render_template, request

# --- Load Trained Model ---
model_path = "model/coral_bleaching_predictor.pkl"
rf_model, alert_level_mapping = joblib.load(model_path)
reverse_mapping = {v: k for k, v in alert_level_mapping.items()}

# --- Define Prediction Function ---
def predict_alert_level(region_lat, region_lon, avg_sst, avg_ph):
    """Predict the coral bleaching alert level for a given region and inputs."""
    features = np.array([[region_lat, region_lon, avg_sst, avg_ph]])
    predicted_label = rf_model.predict(features)[0]
    return reverse_mapping[predicted_label]

# --- Web-based Interface ---
def create_web_interface():
    """Create a web-based interface for map selection and prediction."""
    app = Flask(__name__)

    @app.route('/')
    def index():
        # Main page with mode selection
        return render_template("frame1.html")

    @app.route('/mode', methods=['POST'])
    def mode():
        selected_mode = request.form['mode']
        if selected_mode == "area":
            return render_template("frame2.html")
        elif selected_mode == "point":
            return render_template("frame3.html")

    @app.route('/predict_area', methods=['POST'])
    def predict_area():
        try:
            # Extract inputs
            lat1 = float(request.form['lat1'])
            lon1 = float(request.form['lon1'])
            lat2 = float(request.form['lat2'])
            lon2 = float(request.form['lon2'])
            lat3 = float(request.form['lat3'])
            lon3 = float(request.form['lon3'])
            lat4 = float(request.form['lat4'])
            lon4 = float(request.form['lon4'])
            avg_sst = float(request.form['sst'])
            avg_ph = float(request.form['ph'])

            # Compute region center (approximation)
            region_lat = np.mean([lat1, lat2, lat3, lat4])
            region_lon = np.mean([lon1, lon2, lon3, lon4])

            # Predict alert level
            alert_level = predict_alert_level(region_lat, region_lon, avg_sst, avg_ph)
            return render_template("frame4.html", result=f"Predicted Alert Level for Area: {alert_level}")
        except Exception as e:
            return render_template("frame4.html", result=f"Error: {e}")

    @app.route('/predict_point', methods=['POST'])
    def predict_point():
        try:
            # Extract inputs
            lat = float(request.form['lat'])
            lon = float(request.form['lon'])
            avg_sst = float(request.form['sst'])
            avg_ph = float(request.form['ph'])

            # Predict alert level
            alert_level = predict_alert_level(lat, lon, avg_sst, avg_ph)
            return render_template("frame4.html", result=f"Predicted Alert Level for Point: {alert_level}")
        except Exception as e:
            return render_template("frame4.html", result=f"Error: {e}")

    app.run(debug=True, port=5000)

# --- Run Application ---
if __name__ == "__main__":
    create_web_interface()

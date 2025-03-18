from flask import Flask, request, jsonify, render_template
import requests
import os
from datetime import datetime, timedelta
from fetch_sun_times import get_sun_times

app = Flask(__name__)

#ESP32_IP = os.getenv("ESP32_IP", "http://10.0.0.24/set_times")
ESP32_IP = os.getenv("ESP32_IP", "http://10.198.25.197/set_times")

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/set_times", methods=["POST"])
def set_times():
    data = request.json
    mode = data.get("mode")
    offset = int(data.get("offset", 0))  # Offset in minutes from sunrise, default to 0
    if mode == "manual":
        sunrise = data.get("sunrise")
        sunset = data.get("sunset")
        if not sunrise or not sunset:
            return jsonify({"error": "Invalid data"}), 400

    elif mode == "sunrise_sunset":
        try:
            sunrise, sunset = get_sun_times()
        except Exception as e:
            return jsonify({"error": f"Failed to fetch sunrise/sunset: {e}"}), 500

        sunrise = apply_offset(sunrise, offset)
        sunset = apply_offset(sunset, offset)
        print(f"Adjusted Sunrise: {sunrise}, Sunset: {sunset}")

    else:
        return jsonify({"error": "Invalid mode"}), 400

    payload = {"mode": mode, "sunrise": sunrise, "sunset": sunset}
    print(f"Sending payload to ESP32: {payload}")

    try:
        response = requests.post(ESP32_IP, json=payload)
        if response.status_code == 200:
            return jsonify({"status": "Times sent to ESP32"})
        else:
            return jsonify({"error": f"Failed to send to ESP32 (status {response.status_code})"}), 500
    except requests.RequestException as e:
        return jsonify({"error": f"Error communicating with ESP32: {e}"}), 500


def apply_offset(base_time, offset_minutes): #offset helper function
    base_dt = datetime.strptime(base_time, "%H:%M:%S")
    adjusted_dt = base_dt + timedelta(minutes=offset_minutes)
    return adjusted_dt.strftime("%H:%M:%S")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
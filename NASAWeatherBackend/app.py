from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone
import os

app = Flask(__name__)
CORS(app)

# 🌐 Home route
@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# 🔐 Meteomatics API credentials
base_url = "https://api.meteomatics.com"
username = "stellar_seekers"
password = "cumXKFPR2KtCt2T70F14"

# 🌍 Geocode location
def geocode(location):
    print("🌍 Geocoding:", location)
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": location, "format": "json", "limit": 1},
            headers={"User-Agent": "weather-app"}
        )
        data = response.json()
        if data:
            lat = float(data[0]['lat'])
            lon = float(data[0]['lon'])
            print("📍 Coordinates:", lat, lon)
            return lat, lon
    except Exception as e:
        print("❌ Geocode error:", e)
    return None, None

# 🕒 Format datetime
def format_custom_time(custom_date):
    try:
        dt = datetime.strptime(custom_date, "%Y-%m-%dT%H:%M")
        dt_utc = dt.replace(tzinfo=timezone.utc)
        formatted = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        print("🕒 Formatted UTC:", formatted)
        return formatted
    except ValueError as e:
        print("❌ Time format error:", e)
        return None

# 🌦️ Fetch weather data
def get_weather(lat, lon, custom_time):
    url = f"{base_url}/{custom_time}/t_2m:C,wind_speed_10m:kmh,precip_1h:mm,relative_humidity_2m:p,precip_probability_1h:p,cloud_cover:p,wind_gusts_10m:kmh,heat_index_2m:C/{lat},{lon}/json?model=mix"
    try:
        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        print("📡 API Status:", response.status_code)
        print("📦 Raw Response:", response.text)

        if response.status_code != 200:
            return None, custom_time.replace("T", " ")

        data = response.json()
        if not data.get("data") or len(data["data"]) < 8:
            print("⚠️ Incomplete weather data")
            return None, custom_time.replace("T", " ")

        return data, custom_time.replace("T", " ")
    except Exception as e:
        print("❌ Weather fetch error:", e)
        return None, custom_time.replace("T", " ")
        return jsonify({
            "location": location,
            "timestamp": timestamp,
            "temp": temp,
            "wind": wind,
            "precip": precip,
            "humidity": humidity,
            "description": description(temp, wind, precip, humidity),
            "life_index": life_index(temp, wind, precip, humidity),
            "precip_probability": precip_prob,
            "cloud_cover": cloud_cover,
            "wind_gusts": wind_gusts,
            "heat_index": heat_index
        })
# 📝 Description generator
def description(temp, wind, precip, humidity):
    desc = []
    desc.append("Very Cold" if temp <= 10 else "Cool" if temp <= 20 else "Warm" if temp <= 30 else "Very Hot")
    desc.append("Windy" if wind >= 20 else "Breezy")
    if precip >= 1: desc.append("Wet")
    if humidity >= 80: desc.append("Uncomfortable")
    return " and ".join(desc)

# 🎯 Life index logic
def life_index(temp, wind, precip, humidity):
    return {
        "🚣‍♀ Rowing": "Not suitable" if wind >= 15 or precip >= 1 else "Suitable",
        "🪁 Flying kite": "Not suitable" if wind < 10 or precip >= 1 else "Suitable",
        "🛹 Skateboard": "Very inappropriate" if precip >= 1 else "Suitable",
        "⛳ Golf": "Very inappropriate" if humidity >= 80 or precip >= 1 else "Suitable",
        "🎣 Fishing": "Inappropriate" if temp >= 32 or precip >= 1 else "Suitable",
        "🌠 Stargazing": "Inappropriate" if humidity >= 80 or precip >= 1 else "Suitable",
        "🎤 Outdoor concert": "More suitable" if temp <= 30 and precip < 1 else "Not suitable",
        "🏖 Beach": "More suitable" if temp >= 28 and humidity <= 70 else "Not suitable",
        "🏔 Hiking": "Suitable" if temp <= 30 and precip < 1 and wind < 20 else "Not suitable",
        "✈ Vacation": "More suitable" if temp >= 25 and precip < 1 and humidity <= 80 else "Not suitable"
    }

# 🔍 Extract helper
def extract(data, index, label):
    try:
        value = data['data'][index]['coordinates'][0]['dates'][0]['value']
        print(f"✅ {label}: {value}")
        return value
    except Exception as e:
        print(f"⚠ Missing {label}:", e)
        return None

# 📬 Weather route
@app.route("/weather", methods=["POST"])
def weather_api():
    try:
        data = request.get_json()
        location = data.get("location")
        custom_date = data.get("datetime")
        print("📥 Request:", location, custom_date)

        custom_time = format_custom_time(custom_date)
        if not custom_time:
            return jsonify({"error": "Invalid date format"}), 400

        lat, lon = geocode(location)
        if not lat or not lon:
            return jsonify({"error": "Location not found"}), 400

        weather, timestamp = get_weather(lat, lon, custom_time)
        if not weather or "data" not in weather:
            return jsonify({"error": "Weather data unavailable"}), 500

        temp        = extract(weather, 0, "Temperature")
        wind        = extract(weather, 1, "Wind Speed")
        precip      = extract(weather, 2, "Precipitation")
        humidity    = extract(weather, 3, "Humidity")
        precip_prob = extract(weather, 4, "Rain Chance")
        cloud_cover = extract(weather, 5, "Cloud Cover")
        wind_gusts  = extract(weather, 6, "Wind Gusts")
        heat_index  = extract(weather, 7, "Heat Index")

        if None in [temp, wind, precip, humidity]:
            return jsonify({"error": "Essential weather data missing"}), 500

        return jsonify({
            "location": location,
            "timestamp": timestamp,
            "temp": temp,
            "wind": wind,
            "precip": precip,
            "humidity": humidity,
            "description": description(temp, wind, precip, humidity),
            "life_index": life_index(temp, wind, precip, humidity),
            "precip_probability": precip_prob,
            "cloud_cover": cloud_cover,
            "wind_gusts": wind_gusts,
            "heat_index": heat_index
        })

    except Exception as e:
        print("❌ Server error:", e)
        return jsonify({"error": "Server error occurred"}), 500

# 🚀 Run server
if __name__ == "__main__":
    if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # fallback for local dev
    app.run(host="0.0.0.0", port=port, debug=True)



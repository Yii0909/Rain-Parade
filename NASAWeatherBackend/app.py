from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone
import os

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

# 🔐 Meteomatics API credentials
base_url = "https://api.meteomatics.com"
username = "stellar_seekers"
password = "cumXKFPR2KtCt2T70F14"

# 🌍 Geocode location
def geocode(location):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format": "json", "limit": 1}
    response = requests.get(url, params=params, headers={"User-Agent": "weather-app"})
    data = response.json()
    if data:
        lat = float(data[0]['lat'])
        lon = float(data[0]['lon'])
        return lat, lon
    return None, None

# 🕒 Format datetime for Meteomatics
def format_custom_time(custom_date):
    try:
        dt = datetime.strptime(custom_date, "%Y-%m-%dT%H:%M")
        dt_utc = dt.replace(tzinfo=timezone.utc)
        return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        print("Invalid format. Use YYYY-MM-DDTHH:MM")
        return None

# 🌦️ Fetch weather data
def get_weather(lat, lon, custom_time):
    url = f"{base_url}/{custom_time}/t_2m:C,wind_speed_10m:kmh,precip_1h:mm,relative_humidity_2m:p,precip_probability_1h:p,cloud_cover:p,wind_gusts_10m:kmh,heat_index_2m:C/{lat},{lon}/json?model=mix"
    try:
        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        print(f"🔗 Request URL: {url}")
        print(f"📡 Response Status: {response.status_code}")

        if response.status_code != 200:
            print("❌ API Error:", response.status_code, response.text)
            return None, custom_time.replace("T", " ")

        data = response.json()
        print("📦 Full API Response:", data)

        if not data.get("data") or len(data["data"]) < 4:
            print("⚠️ Incomplete or missing data")
            return None, custom_time.replace("T", " ")

        return data, custom_time.replace("T", " ")
    except Exception as e:
        print("❌ Request failed:", e)
        return None, custom_time.replace("T", " ")

# 📝 Generate weather description
def description(temp, wind, precip, humidity):
    desc = []
    if temp <= 10: desc.append("Very Cold")
    elif temp <= 20: desc.append("Cool")
    elif temp <= 30: desc.append("Warm")
    else: desc.append("Very Hot")
    desc.append("Windy" if wind >= 20 else "Breezy")
    if precip >= 1: desc.append("Wet")
    if humidity >= 80: desc.append("Uncomfortable")
    return " and ".join(desc)

# 🎯 Life index logic
def life_index(temp, wind, precip, humidity):
    index = {}
    index["🚣‍♀ Rowing"] = "Not suitable" if wind >= 15 or precip >= 1 else "Suitable"
    index["🪁 Flying kite"] = "Not suitable" if wind < 10 or precip >= 1 else "Suitable"
    index["🛹 Skateboard"] = "Very inappropriate" if precip >= 1 else "Suitable"
    index["⛳ Golf"] = "Very inappropriate" if humidity >= 80 or precip >= 1 else "Suitable"
    index["🎣 Fishing"] = "Inappropriate" if temp >= 32 or precip >= 1 else "Suitable"
    index["🌠 Stargazing"] = "Inappropriate" if humidity >= 80 or precip >= 1 else "Suitable"
    index["🎤 Outdoor concert"] = "More suitable" if temp <= 30 and precip < 1 else "Not suitable"
    index["🏖 Beach"] = "More suitable" if temp >= 28 and humidity <= 70 else "Not suitable"
    index["🏔 Hiking"] = "Suitable" if temp <= 30 and precip < 1 and wind < 20 else "Not suitable"
    index["✈ Vacation"] = "More suitable" if temp >= 25 and precip < 1 and humidity <= 80 else "Not suitable"
    return index

# 📬 Weather route
@app.route("/weather", methods=["POST"])
def weather_api():
    data = request.get_json()
    location = data.get("location")
    custom_date = data.get("datetime")
    custom_time = format_custom_time(custom_date)

    if not custom_time:
        return jsonify({"error": "Invalid date format"}), 400

    lat, lon = geocode(location)
    if not lat or not lon:
        return jsonify({"error": "Location not found"}), 400

    weather, timestamp = get_weather(lat, lon, custom_time)
    if not weather or "data" not in weather:
        return jsonify({"error": "Weather data unavailable"}), 500

    def extract(index, label):
        try:
            value = weather['data'][index]['coordinates'][0]['dates'][0]['value']
            print(f"✅ {label}: {value}")
            return value
        except (IndexError, KeyError) as e:
            print(f"⚠ Missing {label}: {e}")
            return None

    temp        = extract(0, "Temperature")
    wind        = extract(1, "Wind Speed")
    precip      = extract(2, "Precipitation")
    humidity    = extract(3, "Humidity")
    precip_prob = extract(4, "Rain Chance")
    cloud_cover = extract(5, "Cloud Cover")
    wind_gusts  = extract(6, "Wind Gusts")
    heat_index  = extract(7, "Heat Index")

    if None in [temp, wind, precip, humidity]:
        return jsonify({"error": "Essential weather data missing"}), 500

    desc = description(temp, wind, precip, humidity)
    life = life_index(temp, wind, precip, humidity)

    return jsonify({
        "location": location,
        "timestamp": timestamp,
        "temp": temp,
        "wind": wind,
        "precip": precip,
        "humidity": humidity,
        "description": desc,
        "life_index": life,
        "precip_probability": precip_prob,
        "cloud_cover": cloud_cover,
        "wind_gusts": wind_gusts,
        "heat_index": heat_index
    })

# 🚀 Run server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)






from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone
import os

app = Flask(__name__)
CORS(app)

# 🔐 Meteomatics credentials
base_url = "https://api.meteomatics.com"
username = "stellar_seekers"
password = "cumXKFPR2KtCt2T70F14"

# 🕒 Format datetime for Meteomatics
def format_custom_time(custom_date):
    try:
        dt = datetime.strptime(custom_date, "%Y-%m-%dT%H:%M")
        dt_utc = dt.replace(tzinfo=timezone.utc)
        return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError as e:
        print("❌ Invalid datetime format:", e)
        return None

# 🌦️ Fetch weather data from Meteomatics
def get_weather(lat, lon, custom_time):
    url = f"{base_url}/{custom_time}/t_2m:C,wind_speed_10m:kmh,precip_1h:mm,relative_humidity_2m:p,precip_probability_1h:p,cloud_cover:p,wind_gusts_10m:kmh,heat_index_2m:C/{lat},{lon}/json?model=mix"
    print("🔗 Requesting:", url)

    try:
        response = requests.get(url, auth=HTTPBasicAuth(username, password))
        print("📡 Response Status:", response.status_code)

        if response.status_code != 200:
            print("❌ API error:", response.text)
            return None

        data = response.json()
        print("📦 Full API Response:", data)

        # Check structure before extracting
        if not data.get("data"):
            print("⚠️ No 'data' field in response")
            return None

        try:
            snapshot = {
                "temp":        data['data'][0]['coordinates'][0]['dates'][0]['value'],
                "wind":        data['data'][1]['coordinates'][0]['dates'][0]['value'],
                "precip":      data['data'][2]['coordinates'][0]['dates'][0]['value'],
                "humidity":    data['data'][3]['coordinates'][0]['dates'][0]['value'],
                "precip_probability": data['data'][4]['coordinates'][0]['dates'][0]['value'],
                "cloud_cover": data['data'][5]['coordinates'][0]['dates'][0]['value'],
                "wind_gusts":  data['data'][6]['coordinates'][0]['dates'][0]['value'],
                "heat_index":  data['data'][7]['coordinates'][0]['dates'][0]['value']
            }
            print("✅ Extracted snapshot:", snapshot)
            return snapshot
        except Exception as e:
            print("⚠️ Data extraction error:", e)
            return None

    except Exception as e:
        print("❌ Request failed:", e)
        return None
        
if not weather:
    print("⚠️ Using fallback weather data")
    weather = {
        "temp": 28,
        "wind": 5,
        "precip": 0,
        "humidity": 75,
        "precip_probability": 60,
        "cloud_cover": 80,
        "wind_gusts": 12,
        "heat_index": 33
    }


# 🏠 Serve frontend
@app.route("/")
def home():
    return render_template("map.html")

# 📬 Weather API route
@app.route("/weather", methods=["POST"])
def weather_api():
    data = request.get_json()
    print("📥 Incoming data:", data)

    location = data.get("location")
    datetime_str = data.get("datetime")
    custom_time = format_custom_time(datetime_str)
    print("📍 Location:", location)
    print("🕒 Custom Time:", custom_time)

    if not location or not custom_time:
        print("❌ Missing location or datetime")
        return jsonify({"error": "Missing location or datetime"}), 400

    # 🌍 Geocode location
    try:
        geo_url = "https://nominatim.openstreetmap.org/search"
        params = {"q": location, "format": "json", "limit": 1}
        geo_response = requests.get(geo_url, params=params, headers={"User-Agent": "weather-app"})
        geo_data = geo_response.json()
        print("📍 Geocode result:", geo_data)

        if not geo_data:
            print("❌ Location not found")
            return jsonify({"error": "Location not found"}), 400

        lat = float(geo_data[0]['lat'])
        lon = float(geo_data[0]['lon'])
        print(f"📍 Coordinates: lat={lat}, lon={lon}")
    except Exception as e:
        print("❌ Geocoding failed:", e)
        return jsonify({"error": "Geocoding failed"}), 500

    # 🌦️ Fetch weather
    weather = get_weather(lat, lon, custom_time)
    if not weather:
        print("❌ Weather data unavailable")
        # Optional: simulate fallback data
        weather = {
            "temp": 28,
            "wind": 5,
            "precip": 0,
            "humidity": 75,
            "precip_probability": 60,
            "cloud_cover": 80,
            "wind_gusts": 12,
            "heat_index": 33
        }

    print("✅ Weather snapshot:", weather)

    # 🎯 Add extras
    weather["location"] = location
    weather["timestamp"] = datetime_str
    weather["description"] = "Warm and breezy"
    weather["life_index"] = {
        "Beach": "More suitable",
        "Hiking": "Suitable",
        "Stargazing": "Inappropriate"
    }

    return jsonify(weather)

# 🚀 Run server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)



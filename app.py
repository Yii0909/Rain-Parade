from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

# API verification for Meteomatics
base_url = "https://api.meteomatics.com"
username = "smkbatulintang_tan_hebe"
password = "cumXKFPR2KtCt2T70F14"

# Convert location name to LatLong
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

# Format custom date input to UTC
def format_custom_time(custom_date):
    try:
        dt = datetime.strptime(custom_date, "%Y-%m-%dT%H:%M")
        dt_utc = dt.replace(tzinfo=timezone.utc)
        return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        print("Invalid format. Please use YYYY-MM-DDTHH:MM")
        return None

# Meteomatics weather API with extended parameters
def get_weather(lat, lon, custom_time):
    url = f"{base_url}/{custom_time}/t_2m:C,wind_speed_10m:kmh,precip_1h:mm,relative_humidity_2m:p/{lat},{lon}/json?model=mix"
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    if response.status_code == 200:
        display = custom_time.replace("T", " ")
        return response.json(), display
    print("Error:", response.status_code, response.text)
    return None, custom_time.replace("T", " ")

# Interpret weather conditions
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

@app.route('/weather', methods=['POST'])
def weather_api():
    data = request.get_json()
    location = data['location']
    custom_date = data['datetime']
    custom_time = format_custom_time(custom_date)

    if not custom_time:
        return jsonify({"error": "Invalid date format"}), 400

    lat, lon = geocode(location)
    if not lat or not lon:
        return jsonify({"error": "Location not found"}), 400

    weather, timestamp = get_weather(lat, lon, custom_time)
    if not weather:
        return jsonify({"error": "Weather data unavailable"}), 500

    temp = weather['data'][0]['coordinates'][0]['dates'][0]['value']
    wind = weather['data'][1]['coordinates'][0]['dates'][0]['value']
    precip = weather['data'][2]['coordinates'][0]['dates'][0]['value']
    humidity = weather['data'][3]['coordinates'][0]['dates'][0]['value']
    desc = description(temp, wind, precip, humidity)

    return jsonify({
        "location": location,
        "timestamp": timestamp,
        "temp": temp,
        "wind": wind,
        "precip": precip,
        "humidity": humidity,
        "description": desc
    })

if __name__ == "__main__":
    app.run(debug=True)

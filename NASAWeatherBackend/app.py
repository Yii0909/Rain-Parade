from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

base_url = "https://api.meteomatics.com"
username = "stellar_seekers"
password = "cumXKFPR2KtCt2T70F14"

def format_custom_time(custom_date):
    try:
        dt = datetime.strptime(custom_date, "%Y-%m-%dT%H:%M")
        dt_utc = dt.replace(tzinfo=timezone.utc)
        return dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return None

def get_weather(lat, lon, custom_time):
    url = f"{base_url}/{custom_time}/t_2m:C,wind_speed_10m:kmh,precip_1h:mm,relative_humidity_2m:p,precip_probability_1h:p,cloud_cover:p,wind_gusts_10m:kmh,heat_index_2m:C/{lat},{lon}/json?model=mix"
    response = requests.get(url, auth=HTTPBasicAuth(username, password))
    print(f"🔗 Request URL: {url}")
    print(f"📡 Response Status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            return {
                "temp":        data['data'][0]['coordinates'][0]['dates'][0]['value'],
                "wind":        data['data'][1]['coordinates'][0]['dates'][0]['value'],
                "precip":      data['data'][2]['coordinates'][0]['dates'][0]['value'],
                "humidity":    data['data'][3]['coordinates'][0]['dates'][0]['value'],
                "precip_prob": data['data'][4]['coordinates'][0]['dates'][0]['value'],
                "cloud_cover": data['data'][5]['coordinates'][0]['dates'][0]['value'],
                "wind_gusts":  data['data'][6]['coordinates'][0]['dates'][0]['value'],
                "heat_index":  data['data'][7]['coordinates'][0]['dates'][0]['value']
            }
        except Exception as e:
            print("⚠️ Data extraction error:", e)
            return None
    print("❌ API error:", response.status_code)
    return None

@app.route("/")
def home():
    return render_template("map.html")

@app.route("/weather/coords", methods=["POST"])
def weather_by_coords():
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")
    datetime_str = data.get("datetime")
    custom_time = format_custom_time(datetime_str)

    if not lat or not lon or not custom_time:
        return jsonify({"error": "Missing lat/lon or datetime"}), 400

    weather = get_weather(lat, lon, custom_time)
    if not weather:
        return jsonify({"error": "Weather data unavailable"}), 500

    return jsonify(weather)

if __name__ == "__main__":
    app.run(debug=True, port=10000)

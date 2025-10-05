#API
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone

#API verification for Meteomatics
base_url = "https://api.meteomatics.com"

username = "smkbatulintang_tan_hebe"
password = "cumXKFPR2KtCt2T70F14"


#Convert Locatin name to LatLong
def geocode(location):
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": location, "format":"json","limit":1}
    response = requests.get(url, params=params, headers={"User-Agent":"weather-app"})
    data = response.json()

    if data:
        lat = float(data[0]['lat'])
        lon = float(data[0]['lon'])
        return lat,lon
    else:
        return None, None

#get UTC datetime
def get_UTC(user_input=None, default_hour=0):
    if user_input:
        try:
            if len(user_input.strip())==10:
                dt = datetime.strptime(user_input, "%Y-%m-%d")
                dt = dt.replace(hour=0, minute=0, tzinfo=timezone.utc)
            else:
                dt = datetime.strptime(user_input, "%Y-%m-%dT%H:%M")
                dt = dt.replace(tzinfo=timezone.utc)
        except ValueError:
            print("Invalid format! Use YYYY-MM-DD or YYYY-MM-DD HH:MM")
            return None
    else:
        dt = datetime.now(timezone.utc)
    
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

#Meteomatics weather API
def get_weather(lat,lon,query_time):
    current_time = get_UTC()
    url = f"{base_url}/{query_time}/t_2m:C,wind_speed_10m:kmh/{lat},{lon}/json?model=mix"
    response = requests.get(url, auth=HTTPBasicAuth(username,password))

    if response.status_code == 200:
        display = query_time.replace("T", " ")
        return response.json(), display
    else:
        print("Error:", response.status_code, response.text)
        return None, query_time.replace("T", " ")

def description(temp,wind):
    description = []
    if temp <=10:
        description.append("Very Cold")
    elif temp <=20:
        description.append("Cool")
    elif temp <= 30:
        description.append("Warm")
    else:
        description.append("Very Hot")
    if wind >= 20:
        description.append("Windy")
    else:
        description.append("Breezy")
    return " and ".join(description)
  

#Body code
location = input("Location:")
user_input = input("Date (YYYY-MM-DD) or Date & Time (YYYY-MM-DD HH:MM), leave blank for current time: ").strip()

lat,lon = geocode(location)

if lat and lon:
    utc_time = get_UTC(user_input)
    if utc_time:
        weather,timestamp = get_weather(lat,lon, utc_time)
        if weather:
            temp = weather['data'][0]['coordinates'][0]['dates'][0]['value']
            wind = weather['data'][1]['coordinates'][0]['dates'][0]['value']
            desc = description(temp,wind)
            print(f"Location: {location}")
            print(f"Date and Time/(UTC): {timestamp}")
            print(f"Temperature: {temp}°C")
            print(f"Wind: {wind}km/h")
            print(f"Weather: {desc}")
else:
    print("Could not find the location.")




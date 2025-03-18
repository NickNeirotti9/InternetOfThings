import requests
import json
from datetime import datetime, timedelta

LAT = "38.898049"  # latitude
LON = "-77.051136"  # longitude

API_URL = f"https://api.sunrise-sunset.org/json?lat={LAT}&lng={LON}&formatted=0"

def get_sun_times():
    response = requests.get(API_URL)
    if response.status_code == 200:
        data = response.json()
        sunrise = data['results']['sunrise']
        sunset = data['results']['sunset']
        return convert_to_local(sunrise), convert_to_local(sunset)
    else:
        raise Exception("API Fetch Failed")

def convert_to_local(utc_time):
    utc = datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%S%z')
    local_time = utc - timedelta(hours=5)  # timezone adjust
    return local_time.strftime('%H:%M:%S')

sunrise, sunset = get_sun_times()
print(f"Sunrise: {sunrise}, Sunset: {sunset}")
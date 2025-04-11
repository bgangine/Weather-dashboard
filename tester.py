import os
# Set the environment variable manually for testing purposes
os.environ["OPENWEATHER_API_KEY"] = "45e97eb6e5e89357830f2a793be16338"

print("OPENWEATHER_API_KEY:", os.getenv("OPENWEATHER_API_KEY"))

from backend.utils.weather_api import fetch_weather_data

print("Fetching weather data for London...")
result = fetch_weather_data("London")
print(result)

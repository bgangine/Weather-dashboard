import requests

def fetch_weather_data(city):
    """
    Fetches current weather data from the OpenWeather API
    for the specified city. This version hardcodes the API key
    so it will work without needing environment variables.

    NOTE: The free OpenWeather 'current weather' API does NOT provide
    historical data for arbitrary dates. You must use their One Call API
    (paid) or another service for true historical data.
    """
    # Hardcode your API key directly here:
    api_key = "45e97eb6e5e89357830f2a793be16338"
    
    # Basic validation: If it's empty or None, return an error
    if not api_key:
        return {"error": "API key is missing or empty."}
    
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()  # Raises an HTTPError if status != 200
        data = response.json()
        
        return {
            "temperature": data["main"].get("temp"),
            "humidity": data["main"].get("humidity"),
            "wind_speed": data["wind"].get("speed"),
            "air_quality": None,  # Not provided by the basic endpoint
            "uv_index": None,     # Not provided by the basic endpoint
            "latitude": data["coord"].get("lat"),
            "longitude": data["coord"].get("lon")
        }
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch weather data: {str(e)}"}

import requests

class APIService:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast?"

    
    def fetch_weather(self, city):
        params = {'q': city, 'appid': self.api_key, 'units': 'metric'}
        weather_data = requests.get(self.base_url, params=params)
       # print ("response from API" + weather_data.json())
        return self.parse_response(weather_data.json())
    
    

    def parse_response(self, weather_data):
        return {
            'temperature': weather_data['main']['temp'],
            'humidity': weather_data['main']['humidity'],
            'description': weather_data['weather'][0]['description'],
        }
    
   
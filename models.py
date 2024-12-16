import requests
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime
import time

import mysql.connector

mydb = mysql.connector.connect(
   
  host="localhost",
  user="Shyam13HA",
  password="Shyam1234@",
  database = "mydatabase"
  
)
mycursor = mydb.cursor()
sql =''


class WeatherService:
    """Class to fetch weather data from OpenWeatherMap API."""
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.weather_data = None
        self.icon_url = None
        data= None
        self.holiday_message= "It might be cold"


    def get_weather(  self, city):
        """Fetches weather data for a city."""
        params = {
            'q': city,
            'appid': self.api_key,
            'units': 'metric'
        }
        try:

            response = requests.get(self.base_url, params=params)
            if response.status_code == 200:
                data = response.json()                
                now = datetime.now()
                icon_code = data['weather'][0]['icon']
                temp = round(data['main']['temp'])
                print(temp)
                if(temp > 20):holiday_message = "The weather condition is nice for a holiday :)"
                else:holiday_message = "It is a bit cold out there for a holiday :("
            else: return None

            return {
                'city': data['name'],
                'temperature': round(data['main']['temp']),
                'description': data['weather'][0]['description'],
                'WindSpeed': round(data['wind']['speed']),
                'date': now.strftime("%m/%d/%Y %H:%M:%S"),
                'icon_url' : f'http://openweathermap.org/img/wn/{icon_code}@2x.png',
                'holiday_message' : holiday_message,   
            } 
               
        
    
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None

    def get_weather_icon_url(self):
        """Get the URL for the weather icon."""
        if self.weather_data:
            icon_code = self.weather_data['weather'][0]['icon']
            return f'https://openweathermap.org/img/wn/{icon_code}@2x.png'
        return None

class SearchHistory:
    """Class to handle search history stored in MySQL."""
    @staticmethod
    def store_search(city, temperature, description):
        
        c = mycursor
        ts = time.time()
        City=str(city)
        Temperature=str(temperature)
        Description=str(description)
        print ("adding these", City, Temperature, Description)
        #timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        timestamp = datetime.now()
        
        sql = "INSERT INTO mydatabase.searches( city, temperature, description, timestamp ) VALUES(%s, %s,%s,%s)"
        values = (City, Temperature, Description,timestamp)
        c.execute(sql, values)
        mydb.commit()

    @staticmethod
    def get_all_searches():
       # conn = sqlite3.connect('weather.db')
        
        c = mycursor
        c.execute("SELECT city, temperature, description, timestamp FROM searches ORDER BY timestamp DESC")
        rows = c.fetchall()
        #mydb.close()
        return rows

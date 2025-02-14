import requests
from flask import session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from datetime import datetime
import time
from weatherService import APIService
import mysql.connector

mydb = mysql.connector.connect(
   
  host="localhost",
  user="Shyam13HA",
  password="Shyam1234@",
  database = "mydatabase"
  
)
mycursor = mydb.cursor(buffered=True)
temp_by_date = {}
forecast_data = ''

sql =''
icon_filenames = {"01d": "clear",
                  "01n": "nt_clear",
                  "02d": "cloudy",
                  "02n": "cloudy",
                  "03d": "cloudy",
                  "03n": "cloudy",
                  "04d": "cloudy",
                  "04n": "cloudy",
                  "09d": "chancerain",
                  "09n": "chancerain",
                  "10d": "rain",
                  "10n": "rain",
                  "11d": "tstorms",
                  "11n": "tstorms",
                  "13d": "snow",
                  "13n": "snow",
                  "50d": "fog",
                  "50n": "fog", }


class WeatherService (APIService):
    """Class to fetch weather data from OpenWeatherMap API."""
    def __init__(self, api_key):
        super().__init__(self)
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast?"
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

            weather_data = requests.get(self.base_url, params=params)
            forecast_data = self.fetch_forcast(city)
            weather_by_date = self.get_max_min_temp(forecast_data)
            print ("weather_by_date",weather_by_date)
            
            if weather_data.status_code == 200:
                data = weather_data.json()                
                now = datetime.now()
                icon_code = data['weather'][0]['icon']
                temp = round(data['main']['temp'])
                print(temp)
                if(temp > 20):holiday_message = "The weather condition is nice for a holiday :)"
                else:holiday_message = "It is a bit cold out there for a holiday :("
            else: return None

            return (
                data['name'],
                round(data['main']['temp']),
                data['weather'][0]['description'],
                round(data['wind']['speed']),
                now.strftime("%m/%d/%Y %H:%M:%S"),
                f'http://openweathermap.org/img/wn/{icon_code}@2x.png',
                holiday_message,   
                weather_by_date
            )               
        
    
        except requests.exceptions.RequestException as e:
            print(f"Error fetching weather data: {e}")
            return None

    def get_weather_icon_url(self):
        """Get the URL for the weather icon."""
        if self.weather_data:
            icon_code = self.weather_data['weather'][0]['icon']
            return f'https://openweathermap.org/img/wn/{icon_code}@2x.png'
        return None
    
    def fetch_forcast(self, city) -> dict:
        params = {'q': city, 'appid': self.api_key, 'units': 'metric'}
        forecast_data = requests.get(self.forecast_url, params=params)
        print("HI Shyam")
        print (forecast_data.json())
        return forecast_data.json()    
    
     
    def get_max_min_temp(self, forecast_data: dict) -> dict:
        """
    Calculate the maximum and minimum temperature for each day from the provided forecast data.

    :param forecast_data: A dictionary containing weather forecast data.
    :type forecast_data: dict
    :return: A dictionary with the maximum and minimum temperature and the corresponding weather icon for each day.
    :rtype: dict
    """
        def most_common_icon(icons):
            items = {}
            for item in icons:
                if item in items:
                    items[item] += 1
                else:
                    items[item] = 1
        # Return the sorted items with a daytime icon as first item if possible
            sorted_items = sorted(items.items(), key=lambda item: (item[0][-1] != 'd', -item[1])) 
            return sorted_items[0][0]
        
        temp_by_date = {}
        for item in forecast_data['list']:
            dt = datetime.fromtimestamp(item['dt'])
            date = dt.date()
            icon = item['weather'][0]['icon']
            if date not in temp_by_date:
                temp_by_date[date] = {'temps': [], 'icons': []}
                temp_by_date[date]['temps'].append(item['main']['temp'])
                temp_by_date[date]['icons'].append(icon)
        print("temp_by_date",temp_by_date)

    # Loop through the dictionary to calculate the max and min temperature for each day
        for date, temps_icons in temp_by_date.items():
            max_temp = round(max(temps_icons['temps']))
            min_temp = round(min(temps_icons['temps']))
            icon = most_common_icon(temps_icons['icons'])
            icon = icon_filenames[icon]
            temp_by_date[date] = {'max_temp': max_temp, 
                              'min_temp': min_temp, 'icon': icon}
        return temp_by_date

class SearchHistory:
    """Class to handle search history stored in MySQL."""
    @staticmethod
    def store_search(city, temperature, description, emailId):
        
        c = mycursor
        ts = time.time()
        City=str(city)
        Temperature=str(temperature)
        Description=str(description)
        

        print ("adding these", City, Temperature, Description)
        #timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        timestamp = datetime.now()
       # sql = "SELECT email FROM mydatabase.user WHERE email = %s"
        #values = (username, )
        #c.execute(sql,values)
       # myresult = c.fetchone()
        #print ("myresult is ", myresult)
        #emailId = myresult[0]
        #print ("email is ", emailId)

        sql = "INSERT INTO mydatabase.searches( city, temperature, description, timestamp , emailId) VALUES(%s, %s,%s,%s, %s)"
        values = (City, Temperature, Description,timestamp, emailId)
        c.execute(sql, values)
        mydb.commit()

    @staticmethod
    def get_all_searches(emailId):
       
       c = mycursor
              
       # print ("email is ", emailId)
       c.execute("SELECT city, temperature, description, timestamp FROM searches INNER JOIN user ON user.email=searches.emailId where email = %s ORDER BY timestamp DESC  ",(emailId,))
       rows = c.fetchall()
       #mydb.close()
       return rows
#
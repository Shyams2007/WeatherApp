from flask import Flask, render_template, request, redirect, url_for, session
from models import WeatherService, SearchHistory
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Shyam13HA'
app.config['MYSQL_PASSWORD'] = 'Shyam1234@'
app.config['MYSQL_DB'] = 'mydatabase'

mysql = MySQL(app)

# Initialize WeatherService with OpenWeatherMap API key
weather_service = WeatherService(api_key='Your_Key')

@app.route('/')
@app.route('/home', methods =['GET', 'POST'])
def home():
   
    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def get_weather():
    city = request.form['city']
    weather_data = weather_service.get_weather(city)
    if weather_data:
        # Store search in history
        print(weather_data)
        SearchHistory.store_search( city, weather_data['temperature'], weather_data['description'])
        return render_template('weather.html', weather=weather_data)
    else:
        return render_template('index.html', error="City not found or API error.")

@app.route('/history')
def history():
    searches = SearchHistory.get_all_searches()
    return render_template('history.html', searches=searches)

if __name__ == '__main__':
    app.run(debug=True)

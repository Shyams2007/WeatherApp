import code
from flask import Flask, render_template, request, redirect, url_for, session
from models import WeatherService, SearchHistory
from authlib.integrations.flask_client import OAuth
from flask_mysqldb import MySQL
import MySQLdb.cursors
import requests
from dotenv import dotenv_values
import os
import re
import json

# Third-party libraries

from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from User import User
from oauthlib.oauth2 import WebApplicationClient

# Configuration

GOOGLE_CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID'
GOOGLE_CLIENT_SECRET = 'GOOGLE_CLIENT_SECRET'
GOOGLE_DISCOVERY_URL = (
    "https://accounts.google.com/.well-known/openid-configuration"
)


app = Flask(__name__)

app.secret_key = os.urandom(24)
env_vars = ""

# User session management setup
# https://flask-login.readthedocs.io/en/latest
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.unauthorized_handler
def unauthorized():
    return "Please login to access this content.", 403

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'Shyam13HA'
app.config['MYSQL_PASSWORD'] = 'Shyam1234@'
app.config['MYSQL_DB'] = 'mydatabase'

mysql = MySQL(app)

# OAuth 2 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

# Flask-Login helper to retrieve a user from our db
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


OPENWEATHER_BASE_URL = "https://api.openweathermap.org/data/2.5/weather?"
OPENWEATHER_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast?"

# Initialize WeatherService with OpenWeatherMap API key
def read_api_key():
    try:
        env_vars = dotenv_values('secret.env')
        print("env_vars", env_vars)
        api_key = env_vars.get('OPENWEATHER_API_KEY')
        return api_key
    except Exception as e:
        print(f"Error: {e}")
        return None

api_key1 = read_api_key()
print("api_key1", api_key1)

weather_service = WeatherService(api_key1)


@app.route('/')
def index():
    if current_user.is_authenticated:
        msg = 'Already Logged in!'
        username= current_user.name
        print("username", username)
        emailid= current_user.email
        print("emailid", emailid)
        return render_template('index.html', msg = msg, username=username, emailid=emailid )
        return (
            "<p>Hello, {}! You're logged in! Email: {}</p>"
            "<div><p>Google Profile Picture:</p>"
            '<img src="{}" alt="Google profile pic"></img></div>'
            '<a class="button" href="/logout">Logout</a>'.format(
                current_user.name, current_user.email, current_user.profile_pic
            )
        )
    else:
        return render_template('login.html')
    #'<a class="button" href="/login">Google Login</a>'

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@app.route('/login', methods =['GET', 'POST'])
def login():
    # Find out what URL to hit for Google login
    if current_user.is_authenticated:
        msg = 'Already Logged in!'
        username= current_user.name
        print("username", username)
        emailid= current_user.email
        print("emailid", emailid)
        return render_template('index.html', msg = msg, username=username, emailid=emailid )
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

def login1():
    
    if session.get('logged_in') == True:
        msg = 'Already Logged in!'
        return render_template('index.html', msg = msg)
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            session['logged_in'] = True
            return render_template('index.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg = msg)

@app.route("/login/callback")
def callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code,
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that we have tokens (yay) let's find and hit URL
    # from Google that gives you user's profile information,
    # including their Google Profile Image and Email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # We want to make sure their email is verified.
    # The user authenticated with Google, authorized our
    # app, and now we've verified their email through Google!
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in our db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add to database
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    # Send user back to homepage
    return redirect(url_for("index"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("index"))

@app.route('/logout1')
def logout1():
    session.pop('logged_in', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))
 
@app.route('/register', methods =['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg = msg)

#@app.route('/home', methods =['GET', 'POST'])
#def home():
   
#    return render_template('index.html')

@app.route('/weather', methods=['POST'])
def get_weather():
    
    city = request.form['city']
    weather_data = weather_service.get_weather(city)
    if weather_data:
        # Store search in history
        print("weather_data is -------------------------------------------------",weather_data)
        username = session.get('username')
        print("username is" , username)
        SearchHistory.store_search( city, weather_data[1], weather_data[2], current_user.email)
        return render_template('weather.html', weather=weather_data)
    else:
        return render_template('index.html', error="City not found or API error.")

@app.route('/history')
def history():
    if current_user.is_authenticated:
        msg = 'Already Logged in!'
        username= current_user.name
        print("username", username)
        emailid= current_user.email
        print("emailid", emailid)
        searches = SearchHistory.get_all_searches(emailid)
        return render_template('history.html', searches=searches)
        
    else :
        msg = 'Please Log in to check the weather!'
        return render_template('login.html', msg = msg) 
      
    


if __name__ == '__main__':
    app.run(ssl_context="adhoc")

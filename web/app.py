from curses import flash
from flask import Flask, render_template, request, redirect, url_for, session
from flask_pymongo import PyMongo
from flask_oauthlib.client import OAuth
import requests
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/your_database_name'
app.config['GOOGLE_ID'] = 'your_google_client_id'
app.config['GOOGLE_SECRET'] = 'your_google_client_secret'

mongo = PyMongo(app)

oauth = OAuth(app)
google = oauth.remote_app(
    'google',
    consumer_key=app.config['GOOGLE_ID'],
    consumer_secret=app.config['GOOGLE_SECRET'],
    request_token_params={
        'scope': 'email',
    },
    base_url='https://www.googleapis.com/oauth2/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://accounts.google.com/o/oauth2/token',
    authorize_url='https://accounts.google.com/o/oauth2/auth',
)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    return google.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('home'))

@app.route('/login/authorized')
def authorized():
    response = google.authorized_response()
    if response is None or response.get('access_token') is None:
        flash('Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        ))
        return redirect(url_for('home'))

    session['google_token'] = (response['access_token'], '')
    user_info = google.get('userinfo')
    # Save user_info to the database or use it as needed
    flash('Logged in as: ' + user_info.data['email'])
    return redirect(url_for('home'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/callback')
def callback():
    # Handle OAuth callback here
    # Example: exchange code for access token
    return redirect(url_for('home'))

@app.route('/generate_recipe', methods=['GET', 'POST'])
def generate_recipe():
    if request.method == 'POST':
        # Extract ingredients from the form
        ingredients = request.form.get('ingredients')

        # Make a call to the Edamam API
        edamam_data = requests.get(f'https://api.edamam.com/search?q={ingredients}&app_id=YOUR_APP_ID&app_key=YOUR_APP_KEY').json()

        # Store data in MongoDB
        mongo.db.recipes.insert_one({'edamam': edamam_data, 'ingredients': ingredients})

        return render_template('recipe_result.html', edamam_data=edamam_data)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
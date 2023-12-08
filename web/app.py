from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_oauthlib.client import OAuth
import requests
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['GOOGLE_ID'] = os.getenv('GOOGLE_ID')
app.config['GOOGLE_SECRET'] = os.getenv('GOOGLE_SECRET')
app.config['RECIPE_SEARCH_ID'] = os.getenv('RECIPE_SEARCH_ID')
app.config['RECIPE_SEARCH_KEY'] = os.getenv('RECIPE_SEARCH_KEY')
app.config['NUTRITION_SEARCH_ID'] = os.getenv('NUTRITION_SEARCH_ID')
app.config['NUTRITION_SEARCH_KEY'] = os.getenv('NUTRITION_SEARCH_KEY')

db = SQLAlchemy(app)

# Define the Recipe model
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingredients = db.Column(db.String(500))
    edamam_data = db.Column(db.JSON)

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
    flash('Logged in as: ' + user_info.data['email'])
    return redirect(url_for('home'))

@google.tokengetter
def get_google_oauth_token():
    return session.get('google_token')

@app.route('/generate_recipe', methods=['GET', 'POST'])
def generate_recipe():
    if request.method == 'POST':
        ingredients = request.form.get('ingredients')
        edamam_data = requests.get(f'https://api.edamam.com/search?q={ingredients}&app_id=YOUR_APP_ID&app_key=YOUR_APP_KEY').json()

        new_recipe = Recipe(ingredients=ingredients, edamam_data=edamam_data)
        db.session.add(new_recipe)
        db.session.commit()

        return render_template('recipe_result.html', edamam_data=edamam_data)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
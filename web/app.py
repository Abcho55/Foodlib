from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from authlib.integrations.flask_client import OAuth
import requests
import os
from datetime import datetime
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

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingredients = db.Column(db.String(500))
    recipe_data = db.Column(db.JSON)

class Nutrition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nutrition = db.Column(db.String(500))
    nutrition_data = db.Column(db.JSON)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config['GOOGLE_ID'],
    client_secret=app.config['GOOGLE_SECRET'],
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'email'}
)

@app.context_processor
def inject_current_year():
    return {'current_year': datetime.now().year}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login')
def login():
    redirect_uri = url_for('authorized', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    return redirect(url_for('home'))

@app.route('/login/authorized')
def authorized():
    token = google.authorize_access_token()
    if not token:
        flash('Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        ))
        return redirect(url_for('home'))

    session['google_token'] = token
    resp = google.get('userinfo')
    user_info = resp.json()
    session['user_info'] = user_info
    flash('Logged in as: ' + user_info['email'])
    return redirect(url_for('home'))

# @app.route('/dietary-preferences')
# def dietary_preferences():
#     return render_template('dietary-preferences.html')

@app.route('/ingredient-management')
def ingredient_management():
    # Your logic here
    return render_template('ingredient-management.html')  

# @app.route('/meal-planning')
# def meal_planning():
#     return render_template('meal-planning.html')

@app.route('/nutrition-result')
def nutrition_result():
    # Logic to fetch and pass nutrition data to the template
    return render_template('nutrition-result.html', nutrition_data={})

@app.route('/nutritional-information')
def nutritional_information():
    return render_template('nutritional-information.html')

@app.route('/recipe-result')
def recipe_result():
    # Add logic for recipe exploration page
    return render_template('recipe-result.html')

# @app.route('/recipe-exploration')
# def recipe_exploration():
#     # Add logic for recipe exploration page
#     return render_template('recipe-exploration.html')

@app.route('/generate_recipe', methods=['GET', 'POST'])
def generate_recipe():
    if request.method == 'POST':
        app_id = app.config['RECIPE_SEARCH_ID']
        app_key = app.config['RECIPE_SEARCH_KEY']
        ingredients = request.form.get('ingredients')
        response = requests.get(f'https://api.edamam.com/api/recipes/v2?type=public&q={ingredients}&app_id={app_id}&app_key={app_key}')
        recipe_data = response.json()

        new_recipe = Recipe(ingredients=ingredients, recipe_data=recipe_data)
        db.session.add(new_recipe)
        db.session.commit()

        recipes = recipe_data.get('hits', [])
        return render_template('recipe_result.html', recipes=recipes)

    return render_template('index.html')

@app.route('/generate_nutrition', methods=['GET', 'POST'])
def generate_nutrition():
    if request.method == 'POST':
        app_id = app.config['NUTRITION_SEARCH_ID']
        app_key = app.config['NUTRITION_SEARCH_KEY']
        nutrition = request.form.get('nutrition')
        response = requests.get(f'https://api.edamam.com/api/nutrition-data?q={nutrition}&app_id={app_id}&app_key={app_key}')
        nutrition_data = response.json()

        new_nutrition = Nutrition(nutrition=nutrition, nutrition_data=nutrition_data)
        db.session.add(new_nutrition)
        db.session.commit()

        return render_template('nutrition_result.html', nutrition_data=nutrition_data)
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=True)
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
from spellchecker import SpellChecker
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
migrate = Migrate(app, db) 

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
    print("Generated redirect URI:", redirect_uri)  # Print statement for debugging
    return google.authorize_redirect(redirect_uri)

@app.route('/login/authorized')
def authorized():
    token = google.authorize_access_token()
    if not token:
        flash('Access denied: reason={} error={}'.format(
            request.args['error_reason'],
            request.args['error_description']
        ), 'error')
        return redirect(url_for('home'))
    
    session['google_token'] = token
    resp = google.get('userinfo')
    user_info = resp.json()
    session['user_info'] = user_info
    flash('You are logged in as ' + user_info['email'], 'success')
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.pop('google_token', None)
    session.pop('user_info', None)
    flash('You have been logged out.', 'success')
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

# @app.route('/nutrition-result')
# def nutrition_result():
#     # Logic to fetch and pass nutrition data to the template
#     return render_template('nutrition-result.html', nutrition_data={})

@app.route('/recipe-result')
def recipe_result():
    # Add logic for recipe exploration page
    return render_template('recipe-result.html')

# @app.route('/recipe-exploration')
# def recipe_exploration():
#     # Add logic for recipe exploration page
#     return render_template('recipe-exploration.html')

def correct_spelling(ingredients):
    spell = SpellChecker()
    corrected_ingredients = []
    for ingredient in ingredients:
        words = ingredient.split()  # Split by spaces to check each word in the ingredient
        misspelled = spell.unknown(words)
        corrected = [spell.correction(word) if word in misspelled else word for word in words]
        corrected_ingredients.append(' '.join(corrected))
    return corrected_ingredients

@app.route('/ingredient-management', methods=['GET', 'POST'])
def generate_recipe():
    if request.method == 'POST':
        app_id = app.config['RECIPE_SEARCH_ID']
        app_key = app.config['RECIPE_SEARCH_KEY']
        ingredients = request.form.get('ingredients')
        ingredients_list = [ing.strip() for ing in ingredients.split(',')]  # Split by commas and strip whitespace
        
        corrected_ingredients = correct_spelling(ingredients_list)
        corrected_ingredients_str = ', '.join(corrected_ingredients)  # Rejoin the list into a string

        # Check if corrections were made
        if corrected_ingredients_str != ingredients:
            flash(f"Please check the spelling. Did you mean: {corrected_ingredients_str}?", 'warning')
            return render_template('ingredient-management.html')

        # API request with corrected ingredients
        response = requests.get(
            f'https://api.edamam.com/api/recipes/v2?type=public&q={corrected_ingredients_str}&app_id={app_id}&app_key={app_key}'
        )
        recipe_data = response.json()

        # Assuming you have a Recipe model defined with an ingredients field
        new_recipe = Recipe(ingredients=corrected_ingredients_str, recipe_data=recipe_data)
        db.session.add(new_recipe)
        db.session.commit()

        recipes = recipe_data.get('hits', [])
        return render_template('recipe_result.html', recipes=recipes)

    return render_template('ingredient-management.html')  # Render the page initially

@app.route('/nutritional-information', methods=['GET', 'POST'])
def nutritional_information():
    nutrition_data = None
    data_available = False

    if request.method == 'POST':
        app_id = app.config['NUTRITION_SEARCH_ID']
        app_key = app.config['NUTRITION_SEARCH_KEY']
        nutrition = request.form.get('nutrition')
        nutrition_list = [nutr.strip() for nutr in nutrition.split(',')]  # Split by commas and strip whitespace
        
        corrected_nutrition = correct_spelling(nutrition_list)
        corrected_nutrition_str = ', '.join(corrected_nutrition)  # Rejoin the list into a string

        # Check if corrections were made
        if corrected_nutrition_str != nutrition:
            flash(f"Please check the spelling. Did you mean: {corrected_nutrition_str}?", 'warning')
            return render_template('nutritional-information.html', nutrition_data=None, data_available=False)

        # API request with corrected nutrition
        response = requests.get(
            f'https://api.edamam.com/api/nutrition-data?ingr={corrected_nutrition_str}&app_id={app_id}&app_key={app_key}'
        )
        nutrition_data = response.json()

        if 'error' not in nutrition_data and 'totalNutrients' in nutrition_data:
            data_available = True
            # Assuming you have a Nutrition model defined with a nutrition field
            new_nutrition = Nutrition(nutrition=corrected_nutrition_str, nutrition_data=nutrition_data)
            db.session.add(new_nutrition)
            db.session.commit()
        else:
            flash("No nutritional data found for the given ingredients.", 'warning')

    return render_template('nutritional-information.html', nutrition_data=nutrition_data, data_available=data_available)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, use_reloader=True)
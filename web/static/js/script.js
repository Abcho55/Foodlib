// script.js

// Function to handle adding ingredients
function addIngredient() {
    const ingredientInput = document.getElementById('ingredient-input');
    const ingredientList = document.getElementById('ingredient-list');
    const ingredient = ingredientInput.value.trim();

    if (ingredient) {
        const listItem = document.createElement('li');
        listItem.textContent = ingredient;
        ingredientList.appendChild(listItem);
    }
}

// Function to fetch recipes based on ingredients
function fetchRecipes() {
    const ingredientListItems = document.querySelectorAll('#ingredient-list li');
    const ingredients = Array.from(ingredientListItems).map(li => li.textContent);

    // Replace '/fetch-recipes' with the actual Flask route you have for fetching recipes
    fetch('/fetch-recipes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ingredients: ingredients }),
    })
    .then(response => response.json())
    .then(data => {
        // Handle the response data
        displayRecipes(data.recipes);
    })
    .catch(error => console.error('Error:', error));
}

// Function to display fetched recipes
function displayRecipes(recipes) {
    const recipesContainer = document.getElementById('recipes-container');
    recipesContainer.innerHTML = ''; // Clear previous results
    recipes.forEach(recipe => {
        const recipeDiv = document.createElement('div');
        recipeDiv.className = 'recipe';
        recipeDiv.textContent = recipe.title; // Adjust according to your data structure
        recipesContainer.appendChild(recipeDiv);
    });
}

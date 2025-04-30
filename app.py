from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)
DATA_FILE = 'recipes.json'

# Funkcija, lai ielādētu receptes
def load_recipes():
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Kļūda, ielādējot datus: {e}")
        return []

# Funkcija, lai saglabātu receptes
def save_recipes(recipes):
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(recipes, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Kļūda, saglabājot datus: {e}")

@app.route('/')
def search_page():
    return render_template('search.html')

@app.route('/search', methods=['POST'])
def search():
    recipes = load_recipes()
    query = request.form['query']
    available = set(x.strip().lower() for x in query.split(','))
    results = []

    for r in recipes:
        ing_names = {i['name'].lower() for i in r['ingredients']}
        missing = list(ing_names - available)
        if ing_names & available:
            results.append((r, missing, len(missing)))

    results.sort(key=lambda x: x[2])
    return render_template('search_results.html', results=results)

@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    if request.method == 'POST':
        recipes = load_recipes()
        name = request.form['name']
        category = request.form['category']
        steps = request.form['steps']
        ingredient_names = request.form.getlist('ingredient_name')
        ingredient_quantities = request.form.getlist('ingredient_quantity')
        ingredient_units = request.form.getlist('ingredient_unit')

        ingredients = []
        for i in range(len(ingredient_names)):
            if ingredient_names[i].strip():
                ingredients.append({
                    'name': ingredient_names[i],
                    'quantity': ingredient_quantities[i],
                    'unit': ingredient_units[i]
                })

        new_id = max((r.get('id', 0) for r in recipes), default=0) + 1
        recipes.append({
            'id': new_id,
            'name': name,
            'category': category,
            'ingredients': ingredients,
            'steps': steps
        })

        save_recipes(recipes)
        return redirect(url_for('show_recipes'))

    return render_template('index.html')

@app.route('/recipes')
def show_recipes():
    recipes = load_recipes()
    return render_template('recipes.html', recipes=recipes)

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    recipes = load_recipes()
    recipe = next((r for r in recipes if r.get('id') == recipe_id), None)
    if not recipe:
        return "Recepte nav atrasta", 404
    return render_template('recipe_detail.html', recipe=recipe)

@app.route('/view/<int:index>')
def view_recipe(index):
    recipes = load_recipes()
    if 0 <= index < len(recipes):
        return render_template('recipe_detail.html', recipe=recipes[index])
    return "Recepte nav atrasta", 404

# ✅ REDIĢĒT
@app.route('/edit/<int:recipe_id>', methods=['GET', 'POST'])
def edit_recipe(recipe_id):
    recipes = load_recipes()
    recipe = next((r for r in recipes if r['id'] == recipe_id), None)
    if not recipe:
        return "Recepte nav atrasta", 404

    if request.method == 'POST':
        recipe['name'] = request.form['name']
        recipe['category'] = request.form['category']
        recipe['steps'] = request.form['steps']
        ingredient_names = request.form.getlist('ingredient_name')
        ingredient_quantities = request.form.getlist('ingredient_quantity')
        ingredient_units = request.form.getlist('ingredient_unit')

        ingredients = []
        for i in range(len(ingredient_names)):
            if ingredient_names[i].strip():
                ingredients.append({
                    'name': ingredient_names[i],
                    'quantity': ingredient_quantities[i],
                    'unit': ingredient_units[i]
                })

        recipe['ingredients'] = ingredients
        save_recipes(recipes)
        return redirect(url_for('show_recipes'))

    return render_template('edit.html', recipe=recipe)

# ✅ DZĒST
@app.route('/delete/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    recipes = load_recipes()
    recipes = [r for r in recipes if r['id'] != recipe_id]
    save_recipes(recipes)
    return redirect(url_for('show_recipes'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


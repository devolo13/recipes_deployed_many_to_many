from flask_app import app
from flask import render_template, redirect, request, session
from flask_app.models.recipe_model import Recipe


# page showing all recipes
@app.route('/recipes')
def logged_in_user_page():
    if 'user_id' in session:
        # we have a user. get the recipes and render the all_recipes page
        recipes = Recipe.get_all()
        user_id = session['user_id']
        user_name = session['first_name']
        return render_template('all_recipes.html', user_id=user_id, user_name=user_name, recipes=recipes)
    else:
        # this user doesn't have access to this page. send them to the login page
        return redirect('/')


# template for getting a user's favorite recipes and rendering that page
@app.route('/users_favorites')
def users_favorites():
    if not 'user_id' in session:
        return redirect('/')
    user_id = session['user_id']
    user_name = session['first_name']
    favorites = Recipe.get_favorites(user_id)
    return render_template('user_favorites.html', favorites=favorites, user_name=user_name, user_id=user_id)


# route for verifying recipe inputs, adding it to the db, then redirecting to all_recipes page
@app.route('/add_recipe', methods=['POST'])
def add_new_recipe():
    # format user inputs into the standard format
    # we get name, description, instructions, date_made, under30 fields
    data = {
        **request.form
    }
    # test if the users inputs were valid
    if Recipe.validate_recipe_inputs(data):
        # if user input was valid, add them to the db and redirect to their page
        data['user_id'] = session['user_id']
        Recipe.save(data)
        return redirect('/recipes')
    else:
        # if user input was not valid, show errors and redirect back to new recipe page
        return redirect('/new_recipe_template')


# template for making new recipes
@app.route('/new_recipe_template')
def new_recipe_template():
    if not 'user_id' in session:
        return redirect('/')
    return render_template('/add_recipe.html')


# page showing a single recipe
@app.route('/recipes/<int:recipe_id>')
def individual_recipe_page(recipe_id):
    if not 'user_id' in session:
        return redirect('/')
    user_name = session['first_name']
    recipe = Recipe.get_by_id(recipe_id)
    favoritors = Recipe.get_favoritors(recipe_id)
    return render_template('/single_recipe.html', user_name=user_name, recipe=recipe, favoritors=favoritors)


# route for adding a user to a recipe's favorites and redirecting back to recipe page
@app.route('/add_favorite_<int:recipe_id>', methods=['POST'])
def add_favorite(recipe_id):
    user_id = session['user_id']
    Recipe.add_favorite(user_id, recipe_id)
    return redirect(f'/recipes/{recipe_id}')


# template for editing recipes
@app.route('/recipes/edit/<int:id>')
def recipe_edit_template(id):
    if not 'user_id' in session:
        return redirect('/')
    recipe = Recipe.get_by_id(id)
    if not recipe.user_id == session['user_id']:
        return redirect('/')
    return render_template('/edit_recipe.html', recipe=recipe)


# route for updating recipes
@app.route('/edit_recipe', methods=["POST"])
def edit_recipe():
    data = {
        **request.form,
        'user_id': session['user_id'],
        'user_name': session['first_name']
    }
    if Recipe.validate_recipe_inputs(data) == False:
        return redirect('/recipes/edit/' + str(data['id']))
    Recipe.edit(data)
    return redirect('/recipes')


# route for deleting a recipe and redirecting to page of all recipes
@app.route('/delete/<int:id>')
def delete_recipe(id):
    Recipe.delete(id)
    return redirect('/recipes')

from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DATABASE
from flask import flash


class Recipe:
    def __init__(self, data):
        self.id = data['id']
        self.name = data['name']
        self.description = data['description']
        self.instructions = data['instructions']
        self.under30 = data['under30']
        self.date_made = data['date_made']
        self.user_name = data['first_name']
        self.user_id = data['user_id']

    # method for adding a new recipe. returns that recipes' id
    @classmethod
    def save(cls, data):
        query = 'INSERT into recipes (name, user_id, description, instructions, under30, date_made) values (%(name)s, %(user_id)s, %(description)s, %(instructions)s, %(under30)s, %(date_made)s);'
        connectToMySQL(DATABASE).query_db(query, data)
        query = 'SELECT MAX(id) from recipes;'
        recipe_id = connectToMySQL(DATABASE).query_db(query)[0]['MAX(id)']
        return recipe_id

    # method for editing a recipe. returns nothing
    @classmethod
    def edit(cls, data):
        query = 'UPDATE recipes SET name = %(name)s, description = %(description)s, instructions = %(instructions)s, date_made = %(date_made)s, under30 = %(under30)s WHERE id = %(id)s;'
        connectToMySQL(DATABASE).query_db(query, data)
        return

    # method for getting all recipes. returns a list of recipe objects
    @classmethod
    def get_all(cls):
        query = 'SELECT recipes.id, user_id, name, description, instructions, under30, date_made, first_name FROM recipes left join users on users.id = recipes.user_id;'
        results = connectToMySQL(DATABASE).query_db(query)
        recipes_list = []
        for recipe in results:
            recipes_list.append(cls(recipe))
        return recipes_list

    # method for getting a single recipe by it's id. returns recipe object
    @classmethod
    def get_by_id(cls, id):
        data = {'id': int(id)}
        query = 'SELECT recipes.id, user_id, name, description, instructions, under30, date_made, first_name FROM recipes left join users on users.id = recipes.user_id WHERE recipes.id = %(id)s'
        results = connectToMySQL(DATABASE).query_db(query, data)
        return cls(results[0])

    # method for getting all people who have favorited a recipe. returns a list with user names
    @classmethod
    def get_favoritors(cls, id):
        data = {'id': int(id)}
        query = 'SELECT first_name FROM recipes LEFT JOIN favorites on favorites.recipe_id = recipes.id LEFT JOIN users on users.id = favorites.user_id WHERE recipes.id = %(id)s;'
        results = connectToMySQL(DATABASE).query_db(query, data)
        return results

    # method for adding a user to a recipe's favoritors
    @classmethod
    def add_favorite(cls, user_id, recipe_id):
        data = {
            'user_id': user_id,
            'recipe_id': recipe_id
        }
        query = 'INSERT into favorites (user_id, recipe_id) VALUES (%(user_id)s, %(recipe_id)s);'
        connectToMySQL(DATABASE).query_db(query, data)
        return

    # method for validating recipe creation. returns True if valid, False if invalid. creates flash messages along the way
    @staticmethod
    def validate_recipe_inputs(data):
        valid_inputs = True
        # validate name length
        if (len(data['name']) < 3):
            flash('Recipe name must be at least 3 characters', 'name')
            valid_inputs = False
        # validate description length
        if (len(data['description']) < 3):
            flash('Recipe description must be at least 3 characters', 'description')
            valid_inputs = False
        # validate instructions length
        if (len(data['instructions']) < 3):
            flash('Recipe instructions must be at least 3 characters', 'instructions')
            valid_inputs = False
        return valid_inputs

    # method for deleting a recipe
    @classmethod
    def delete(cls, id):
        data = {'id': id}
        query = 'DELETE from recipes where id = %(id)s;'
        connectToMySQL(DATABASE).query_db(query, data)
        return

    # method for getting all recipes by user_id. returns a list of recipe objects
    @classmethod
    def get_favorites(cls, user_id):
        data = {'user_id': int(user_id)}
        query = 'SELECT recipes.id, favorites.user_id, name, description, instructions, under30, date_made, first_name FROM recipes LEFT JOIN favorites on favorites.recipe_id = recipes.id LEFT JOIN users on users.id = favorites.user_id WHERE favorites.user_id = %(user_id)s;'
        results = connectToMySQL(DATABASE).query_db(query, data)
        recipes_list = []
        for recipe in results:
            recipes_list.append(cls(recipe))
        return recipes_list
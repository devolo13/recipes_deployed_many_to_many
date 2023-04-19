from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import DATABASE, app
from flask import flash
from flask_bcrypt import Bcrypt
import re

bcrypt = Bcrypt(app)


class User:
    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']

    # method for adding a new user. returns that user's object
    @classmethod
    def save(cls, data):
        query = 'INSERT into users (first_name, last_name, email, password) values (%(first_name)s, %(last_name)s, %(email)s, %(password)s);'
        connectToMySQL(DATABASE).query_db(query, data)
        query = 'select * from users where id = (select MAX(id) from users);'
        user = connectToMySQL(DATABASE).query_db(query)[0]
        return cls(user)

    # method for getting all users. returns a list of user objects
    @classmethod
    def get_all(cls):
        query = 'SELECT * FROM users;'
        results = connectToMySQL(DATABASE).query_db(query)
        users = []
        for user in results:
            users.append(cls(user))
        return users

    # method for getting a single user by their id. returns user object
    @classmethod
    def get_by_id(cls, id):
        data = {'id': int(id)}
        query = 'SELECT * FROM users WHERE id = %(id)s'
        results = connectToMySQL(DATABASE).query_db(query, data)
        return cls(results[0])

    # method for getting all user logins. returns a list of dictionaries. [{email: xxx, password: xxx, id: xxx}]
    @classmethod
    def get_all_logins(cls):
        query = "SELECT email, password, id FROM users;"
        results = connectToMySQL(DATABASE).query_db(query)
        logins = []
        for person in results:
            logins.append(person)
        return logins

    # method for determining if an email is already in use. returns user object if email is found, returns false if email is not found
    @classmethod
    def check_email(cls, email):
        data = {'email': email}
        query = 'SELECT * from users where email = %(email)s;'
        results = connectToMySQL(DATABASE).query_db(query, data)
        if results == []:
            return False
        return cls(results[0])

    # method for validating user registration inputs. returns True if valid, False if invalid. creates flash messages along the way
    @staticmethod
    def validate_registration_inputs(data):
        valid_inputs = True
        # validate first name length
        if (len(data['first_name']) < 2):
            flash('First name too short. Please input your name', 'first_name')
            valid_inputs = False
        # validate last name length
        if (len(data['last_name']) < 2):
            flash('Last name too short. Please input your name', 'last_name')
            valid_inputs = False
        # validate email format
        if not re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$').match(data['email']):
            flash('Please input a valid email address', 'register_email')
            valid_inputs = False
        # validate email doesn't exist in db
        if User.check_email == False:
            flash('This email is already in use', 'register_email')
            valid_inputs = False
        # validate password length
        if (len(data['password']) <= 8):
            flash('Password too short. Passwords must be at least 8 characters', 'register_password')
            valid_inputs = False
        # validate password confirmation
        if data['password'] != data['confirm_password']:
            flash('Passwords do not match', 'confirm_password')
            valid_inputs = False
        return valid_inputs


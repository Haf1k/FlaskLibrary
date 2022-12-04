import bcrypt
from flask import render_template, url_for, request, redirect
from flask_login import login_user, current_user
from wtforms import ValidationError
from run import app, login_manager
from forms import RegistrationForm
from config import db
from models import User


@app.route('/')
def home():
    return render_template('home.html')

@login_manager.user_loader
def load_user(user):
    return User.query.get(int(user))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
       return redirect(url_for('home'))
    if request.method == 'POST':
        user = db.users.find_one({'username': request.form['username']})

        if user and bcrypt.checkpw(request.form['password'],user['password'],):
            login_user(user, True)
            return render_template('home.html')
        else:
           return "Neuspech. Spatne heslo nebo jmeno."
        return render_template('login.html')
    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        user_exist = db.users.find_one({'username': request.form['username'],
                                        'birthnum': request.form['birthnum']})
        if user_exist is None:
            hashPassword = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            user = User(request.form['fname'],
                        request.form['lname'],
                        request.form['birthnum'],
                        request.form['email'],
                        request.form['street'],
                        request.form['city'],
                        request.form['zip'],
                        request.form['username'],
                        hashPassword)
            db.users.insert_one(user.__dict__)
            return redirect(url_for('home'))
        ValidationError('Nejde to. Uzivatel jiz existuje.')
        return render_template('register.html')
    return render_template('register.html')


@app.route('/about')
def about():
    return render_template('about.html')

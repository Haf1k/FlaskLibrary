import bcrypt
from flask import render_template, url_for, request, redirect
from flask_login import login_user, current_user
from wtforms import ValidationError
from run import app, login_manager
from forms import RegistrationForm, LoginForm
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
    form = LoginForm(csrf_enabled=False)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # if request.method == 'POST':
    if form.validate_on_submit():
        user = db.users.find_one({'username': form.username.data})

        if user and bcrypt.checkpw(form.password.data.encode('utf-8'), user['password'], ):
            # login_user(user, True)
            return "<h1>Úspěšně přihlášeno</h1>"
        else:
            return "Neuspech. Spatne heslo nebo jmeno."
    return render_template('login.html', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    # if request.method == "POST":
    form = RegistrationForm(csrf_enabled=False)
    if form.validate_on_submit():
        user_exist = db.users.find_one({'username': form.username.data,
                                        'birthnum': form.birthnum.data})
        if user_exist is None:
            hashPassword = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
            user = User(form.fname.data,
                        form.lname.data,
                        int(form.birthnum.data),
                        form.email.data,
                        form.street.data,
                        form.city.data,
                        form.zip.data,
                        form.username.data,
                        hashPassword)
            db.users.insert_one(user.__dict__)
            return redirect(url_for('home'))
        ValidationError('Nejde to. Uzivatel jiz existuje.')
        return render_template('register.html', form=form)
    return render_template('register.html', form=form)


@app.route('/about')
def about():
    return render_template('about.html')

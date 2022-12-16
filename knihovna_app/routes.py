import bcrypt
from flask import render_template, url_for, request, redirect, abort, flash
from flask_login import login_user, current_user, login_required, logout_user
from wtforms import ValidationError
from run import app, login_manager
from forms import RegistrationForm, LoginForm, CreateBookForm
from config import db
from models import User, Book
from helper import make_user_object



@app.route('/')
def home():
    return render_template('home.html')


@login_manager.user_loader
def load_user(user):
    u = db.users.find_one({"username": user})
    if not u:
        return None
    return make_user_object(u)


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm(csrf_enabled=False)
    if current_user.is_authenticated:
        return redirect(url_for('user_section', username=current_user.username))
    # if request.method == 'POST':
    if form.validate_on_submit():
        user = db.users.find_one({'username': form.username.data})

        if user and bcrypt.checkpw(form.password.data.encode('utf-8'), user['password'], ):
            user_obj = make_user_object(user)
            login_user(user_obj, True)
            return redirect(url_for('user_section', username=user_obj.username))
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


@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user_section(username):
    if username != current_user.username:
        abort(403)
    book_form = CreateBookForm(csrf=False)
    if book_form.validate_on_submit():
        book = Book(book_form.title.data,
                    book_form.author.data,
                    book_form.release_year.data,
                    book_form.num_pages.data,
                    book_form.num_pcs.data,
                    book_form.picture.data,
                    book_form.available.data)
        db.books.insert_one(book.__dict__)
    return render_template('user_section.html', book_form=book_form)

@app.route('/user/<username>/library_catalog', methods=['GET', 'POST'])
@login_required
def library_catalog(username):
    if username != current_user.username:
        abort(403)
    books = db.books.find({})
    return render_template('library_catalog.html', books=books)

@app.route('/about')
def about():
    return render_template('about.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

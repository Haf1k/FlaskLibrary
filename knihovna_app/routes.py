from datetime import datetime
import bcrypt
import bson
import pymongo
from bson import ObjectId
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
        return redirect(url_for('user_section'))
    # if request.method == 'POST':
    if form.validate_on_submit():
        user = db.users.find_one({'username': form.username.data})

        if user and bcrypt.checkpw(form.password.data.encode('utf-8'), user['password'], ):
            user_obj = make_user_object(user)
            login_user(user_obj, True)
            return redirect(url_for('user_section'))
        else:
            flash("Špatné jméno nebo heslo", "danger")
    return render_template('login.html', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    # if request.method == "POST":
    form = RegistrationForm(csrf_enabled=False)
    if form.validate_on_submit():
        try:
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
            user = user.__dict__
            user['_id'] = ObjectId()
            db.users.insert_one(user)
            flash("Uživatel úspěšně vytvořen", "success")
            return redirect(url_for('home'))
        except:
            flash("Uživatel s tímto uživatelským jménem nebo e-mailem již existuje", "danger")
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)


@app.route('/user/', methods=['GET', 'POST'])
@login_required
def user_section():
    book_form = CreateBookForm(csrf=False)
    if book_form.validate_on_submit():
        try:
            book = Book(book_form.title.data,
                        book_form.author.data,
                        book_form.release_year.data,
                        book_form.num_pages.data,
                        book_form.num_pcs.data,
                        book_form.picture.data,
                        book_form.available.data)
            db.books.insert_one(book.__dict__)
            flash("Kniha úspěšně přidána", "success")
        except:
            flash("Chyba při přidávání knihy", "danger")
    return render_template('user_section.html', book_form=book_form)


@app.route('/user/library_catalog', methods=['GET', 'POST'])
@login_required
def library_catalog():
    borrowed_books = []
    books = db.books.find({}).sort([("author", pymongo.ASCENDING)])
    borrowed_books_helper = db.users.find_one({"username": current_user.username})
    borrowed_books_helper = set().union(*(book.keys() for book in borrowed_books_helper["borrowed_books"])) #kill me pls
    for each in borrowed_books_helper:
        borrowed_books.append(db.books.find_one({"_id": ObjectId(each)}))

    return render_template('library_catalog.html', books=books, borrowed_books=borrowed_books)


@app.route('/user/library_catalog/rent/<book_id>', methods=['GET', 'POST'])
@login_required
def rent(book_id):

    if any(book_id in book for book in current_user.borrowed_books):
        flash("Knihu již máte zapůjčenou.", 'danger')
    elif len(current_user.borrowed_books)>5:
        flash("Již máte zapůjčený maximální počet knih.", "danger")
    else:
        db.users.update_one(
            {"username" : current_user.username},
            {"$push": {"borrowed_books" : {str(book_id) : datetime.now()} }}
        )
        flash("Kniha úspěšně zapůjčena.", 'success')
    return redirect(url_for('library_catalog'))

# @app.route('/user/library_catalog/give_back/<book_id>', methods=['GET', 'POST'])
# @login_required
# def give_back(book_id):
#
#     if any(book_id in book for book in current_user.borrowed_books):
#         flash("Knihu již máte zapůjčenou.", 'danger')
#     elif len(current_user.borrowed_books)>5:
#         flash("Již máte zapůjčený maximální počet knih.", "danger")
#     else:
#         db.users.update_one(
#             {"username" : current_user.username},
#             {"$push": {"borrowed_books" : {str(book_id) : datetime.now()} }}
#         )
#         flash("Kniha úspěšně zapůjčena.", 'success')
#     return redirect(url_for('library_catalog'))

@app.route('/about')
def about():
    return render_template('about.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

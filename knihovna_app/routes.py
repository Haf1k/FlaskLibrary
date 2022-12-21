from datetime import datetime
import bcrypt
import pymongo
from bson import ObjectId
from flask import render_template, url_for, request, redirect, abort, flash
from flask_login import login_user, current_user, login_required, logout_user
from wtforms import ValidationError
from run import app, login_manager
from forms import RegistrationForm, LoginForm, CreateBookForm, EditUser
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
        if user and bcrypt.checkpw(form.password.data.encode('utf-8'), user['password']):
            if not user["activated"]:
                flash("Váš účet není aktivován", "danger")
                return redirect(url_for("login"))
            user_obj = make_user_object(user)
            login_user(user_obj, True)
            return redirect(url_for('library_catalog'))
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
                        form.birthnum.data,
                        form.email.data,
                        form.street.data,
                        form.city.data,
                        form.zip.data,
                        form.username.data,
                        hashPassword)
            user = user.__dict__
            user['_id'] = ObjectId()
            db.users.insert_one(user)
            if current_user.role == "Admin":
                db.users.update_one({"_id": user["_id"]}, {"$set": {"activated": True}})
            flash("Uživatel úspěšně vytvořen", "success")
            return redirect(url_for('home'))
        except:
            flash("Uživatel s tímto uživatelským jménem nebo e-mailem již existuje", "danger")
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)


@app.route('/user/', methods=['GET', 'POST'])
@login_required
def user_section():
    # function for viewing history of account and editing user information
    return render_template("user_section.html")


@app.route('/library_catalog', methods=['GET', 'POST'])
@login_required
def library_catalog():
    if current_user.role == "Admin":
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

        unverified_users = db.users.find({"activated": False})  # .sort(["lname", pymongo.ASCENDING])
        if len(list(unverified_users.clone())) != 0:
            flash(f"Počet uživatelů k ověření: {len(list(unverified_users.clone()))}", "warning")

    books = db.books.find({}).sort([("author", pymongo.ASCENDING)])
    borrowed_books = db.users.find_one({"username": current_user.username})["borrowed_books"]
    borrowed_books = [db.books.find_one({"_id": ObjectId(each["borrowed_book_id"])}) for each in borrowed_books]
    return render_template('library_catalog.html', books=books, borrowed_books=borrowed_books,
                           book_form=book_form, unverified_users=unverified_users)


@app.route('/users_catalog', methods=['GET', 'POST'])
@login_required
def users_catalog():
    if current_user.role != "Admin":
        abort(403)

    users = db.users.find({"role": "user"}).sort([("lname", pymongo.DESCENDING)])
    return render_template("users_catalog.html", users=users)


@app.route('/library_catalog/borrow/<book_id>', methods=['GET', 'POST'])
@login_required
def borrow(book_id):
    if any(book_id in book["borrowed_book_id"] for book in current_user.borrowed_books):
        flash("Knihu již máte zapůjčenou.", 'danger')
    elif len(current_user.borrowed_books) > 5:
        flash("Již máte zapůjčený maximální počet knih.", "danger")
    else:
        db.users.update_one(
            {"username": current_user.username},
            {"$push": {"borrowed_books": {"borrowed_book_id": book_id, "time_stamp": datetime.utcnow()}}}
        )
        flash("Kniha úspěšně zapůjčena.", 'success')
    return redirect(url_for('library_catalog'))


@app.route('/users_catalog/edit_user/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != "Admin":
        abort(403)
    edit_form = EditUser(csrf=False)
    if request.method == 'POST':
        try:
            db.users.update_one({"_id": ObjectId(user_id)},
                                {"$set": {"fname": edit_form.fname.data,
                                          "lname": edit_form.lname.data,
                                          "birthnum": edit_form.birthnum.data,
                                          "email": edit_form.email.data,
                                          "street": edit_form.street.data,
                                          "city": edit_form.city.data,
                                          "zip": edit_form.zip.data,
                                          "username": edit_form.username.data,
                                          "activated": edit_form.activated.data,
                                          "role": edit_form.role.data}})
            flash("Úspěšně upraveno", "success")
        except:
            flash("Nepodařilo se upravit", "warning")

    user = db.users.find_one({"_id": ObjectId(user_id)})
    return render_template("edit_user.html", user=user, edit_form=edit_form)


@app.route('/library_catalog/give_back/<book_id>', methods=['GET', 'POST'])
@login_required
def give_back(book_id):
    db.users.update_one({"username": current_user.username},
                        {"$pull": {"borrowed_books": {"borrowed_book_id": book_id}}})
    return redirect(url_for('library_catalog'))


@app.route('/library_catalog/verify/<user_id>', methods=['GET', 'POST'])
@login_required
def verify(user_id):
    db.users.update_one({"_id": ObjectId(user_id)},
                        {"$set": {"activated": True}})
    return redirect(url_for('library_catalog'))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

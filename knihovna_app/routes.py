from datetime import datetime, timedelta
import bcrypt
import pymongo
from bson import ObjectId
from flask import render_template, url_for, request, redirect, abort, flash
from flask_login import login_user, current_user, login_required, logout_user
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
            hash_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
            user = User(form.fname.data,
                        form.lname.data,
                        form.birthnum.data,
                        form.email.data,
                        form.street.data,
                        form.city.data,
                        form.zip.data,
                        form.username.data,
                        hash_password)
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


@app.route('/user', methods=['GET', 'POST'])
@login_required
def user_section():
    user_id = db.users.find_one({"username": current_user.username})["_id"]
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
                                          "activated": edit_form.activated.data}})
            flash("Úspěšně upraveno", "success")
            return redirect(url_for("logout"))
        except:
            flash("Nepodařilo se upravit", "warning")
            return redirect(url_for("user_section"))

    user = db.users.find_one({"_id": ObjectId(user_id)})
    return render_template("user_section.html", user=user, edit_form=edit_form)


@app.route('/library_catalog', methods=['GET', 'POST'])
@login_required
def library_catalog():
    book_form = CreateBookForm(csrf=False)
    unverified_users = db.users.find({"activated": False})  # .sort(["lname", pymongo.ASCENDING])
    if current_user.role == "Admin":
        if book_form.validate_on_submit():
            try:
                book = Book(book_form.title.data,
                            book_form.author.data,
                            book_form.release_year.data,
                            book_form.num_pages.data,
                            book_form.num_pcs.data,
                            book_form.picture.data,
                            )
                db.books.insert_one(book.__dict__)
                flash("Kniha úspěšně přidána", "success")
            except:
                flash("Chyba při přidávání knihy", "danger")

        if len(list(unverified_users.clone())) != 0:
            flash(f"Počet uživatelů k ověření: {len(list(unverified_users.clone()))}", "warning")

    books = db.books.find({}).sort([("author", pymongo.ASCENDING)])
    borrowed_books = db.users.find_one({"username": current_user.username})["borrowed_books"]
    borrowed_books = [db.books.find_one({"_id": ObjectId(each["borrowed_book_id"])}) for each in borrowed_books]
    return render_template('library_catalog.html', books=books, borrowed_books=borrowed_books,
                           book_form=book_form, unverified_users=unverified_users, user=current_user)


@app.route('/users_catalog', methods=['GET', 'POST'])
@login_required
def users_catalog():
    if current_user.role != "Admin":
        abort(403)

    users = db.users.find({"role": "user"}).sort([("lname", pymongo.DESCENDING)])
    return render_template("users_catalog.html", users=users)


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

    borrowed_books = db.users.find_one({"_id": ObjectId(user_id)})["borrowed_books"]
    borrowed_books = [db.books.find_one({"_id": ObjectId(each["borrowed_book_id"])}) for each in borrowed_books]

    user = db.users.find_one({"_id": ObjectId(user_id)})
    return render_template("edit_user.html", user=user, edit_form=edit_form, borrowed_books=borrowed_books)


@app.route('/library_catalog/edit_book/<book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if current_user.role != "Admin":
        abort(403)
    edit_book_form = CreateBookForm(csrf=False)
    if request.method == 'POST':
        try:
            db.books.update_one({"_id": ObjectId(book_id)},
                                {"$set": {"title": edit_book_form.title.data,
                                          "author": edit_book_form.author.data,
                                          "release_year": edit_book_form.release_year.data,
                                          "num_pages": edit_book_form.num_pages.data,
                                          "num_pcs": edit_book_form.num_pcs.data,
                                          "picture": edit_book_form.picture.data
                                          }})
            flash("Úspěšně upraveno", "success")
        except:
            flash("Nepodařilo se upravit", "warning")
    book = db.books.find_one({"_id": ObjectId(book_id)})

    borrowed_by_users = db.books.find_one({"_id": ObjectId(book_id)})["borrowed_by"]
    borrowed_by_users = [db.users.find_one({"_id": ObjectId(each["user_id"])}) for each in borrowed_by_users]

    return render_template("edit_book.html", edit_book_form=edit_book_form, book=book,
                           borrowed_by_users=borrowed_by_users)


@app.route('/library_catalog/borrow/<username>/<book_id>', methods=['GET', 'POST'])
@login_required
def borrow(book_id, username):
    if current_user.username != username and current_user.role != "Admin":
        abort(403)

    user = make_user_object(db.users.find_one({"username": username}))
    user.borrow_book(book_id)

    if current_user.username != username:
        return redirect(url_for("edit_user", user_id=user.get_string_id()))
    else:
        return redirect(url_for('library_catalog'))


@app.route('/library_catalog/return_book/<book_id>/<username>', methods=['GET', 'POST'])
@login_required
def return_book(book_id, username):
    if current_user.username != username and current_user.role != "Admin":
        abort(403)

    user = make_user_object(db.users.find_one({"username": username}))
    user.return_book(book_id)

    if current_user.username != username:
        return redirect(url_for("edit_user", user_id=str(db.users.find_one({"username": username})["_id"])))
    else:
        return redirect(url_for('library_catalog'))


@app.route('/users_catalog/edit_user/give_user_book/<user_id>', methods=['GET', 'POST'])
@login_required
def give_user_book(user_id):
    if current_user.role != "Admin":
        abort(403)
    books = db.books.find({}).sort([("author", pymongo.ASCENDING)])
    user = db.users.find_one({"_id": ObjectId(user_id)})
    return render_template("give_user_book.html", books=books, user=user)


@app.route('/library_catalog/verify/<user_id>', methods=['GET', 'POST'])
@login_required
def verify(user_id):
    if current_user.role != "Admin":
        abort(403)
    db.users.update_one({"_id": ObjectId(user_id)},
                        {"$set": {"activated": True}})
    return redirect(url_for('library_catalog'))


@app.route('/library_catalog/delete/<book_id>', methods=['GET', 'POST'])
@login_required
def delete_book(book_id):
    if current_user.role != "Admin":
        abort(403)
    if db.books.find_one({"_id": ObjectId(book_id)})["borrowed_by"]:
        flash("Knihu nelze smazat, jelikož ji má někdo půjčenou.", 'danger')
    else:
        db.books.delete_one({"_id": ObjectId(book_id)})
        flash("Kniha byla úspěšně smazána", "success")
    return redirect(url_for("library_catalog"))


@app.route('/users_catalog/delete/<user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    if current_user.role != "Admin":
        abort(403)
    if db.users.find_one({"_id": ObjectId(user_id)})["borrowed_books"]:
        flash("Uživatel nemůže být smazán, jelikož má stále zapůjčené knihy.", 'danger')
    else:
        db.users.delete_one({"_id": ObjectId(user_id)})
        flash("Uživatel byl úspěšně smazán", "success")
    return redirect(url_for("users_catalog"))


@app.route('/about')
def about():
    return render_template('about.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

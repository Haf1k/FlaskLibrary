import io

import bcrypt
from bson import ObjectId
from flask import render_template, url_for, request, redirect, abort, flash, send_file
from flask_login import login_user, current_user, login_required, logout_user

from config import db
from forms import RegistrationForm, LoginForm, CreateBookForm, EditUser, SearchForm
from helper import make_user_object, books_listing, books_borrowed_by_user, users_with_borrowed_book, users_listing, \
    make_book_object, create_book, create_user, library_history, send_image_to_db
from run import app, login_manager


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
    if form.validate_on_submit():
        user = db.users.find_one({'username': form.username.data})
        if user and bcrypt.checkpw(form.password.data.encode('utf-8'), user['password']):
            if not user["activated"]:
                flash("Váš účet není aktivován", "danger")
                return redirect(url_for("login"))
            user_obj = make_user_object(user)
            login_user(user_obj, True)
            return redirect(url_for('library_catalog', sort_value="default", type="asc", search_value="None"))
        else:
            flash("Špatné jméno nebo heslo", "danger")
    return render_template('login.html', form=form)


@app.route('/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm(csrf_enabled=False)
    if form.birthnum.data is None:
        return render_template('register.html', form=form)
    if form.validate_on_submit():
        try:
            hash_password = bcrypt.hashpw(form.password.data.encode('utf-8'), bcrypt.gensalt())
            user = create_user(form, hash_password).__dict__
            user['_id'] = ObjectId()
            db.users.insert_one(user)
            if current_user.role == "Admin":
                db.users.update_one({"_id": user["_id"]}, {"$set": {"activated": True}})
            flash("Uživatel úspěšně vytvořen", "success")
            return redirect(url_for('home'))
        except:
            flash("Uživatel s tímto uživatelským jménem nebo e-mailem již existuje", "danger")
            return render_template('register.html', form=form)
    else:
        flash("Oveřte zadané údaje", "danger")
    return render_template('register.html', form=form)


@app.route('/user', methods=['GET', 'POST'])
@login_required
def user_section():
    user = make_user_object(db.users.find_one({"username": current_user.username}))
    edit_form = EditUser(csrf=False)
    if request.method == 'POST':
        try:
            user.update(edit_form)
            flash("Úspěšně upraveno", "success")
            return redirect(url_for("logout"))
        except:
            flash("Nepodařilo se upravit", "warning")
            return redirect(url_for("user_section"))

    user_history = user.user_history()
    user = db.users.find_one({"_id": ObjectId(user.get_string_id())})

    return render_template("user_section.html", user=user, edit_form=edit_form, user_history=user_history)


@app.route('/library_catalog/<sort_value>/<type>/<search_value>', methods=['GET', 'POST'])
@login_required
def library_catalog(sort_value, type, search_value):
    book_form = CreateBookForm(csrf=False)
    search_form = SearchForm(csrf=False)
    unverified_users = db.users.find({"activated": False})
    if current_user.role == "Admin":
        if book_form.validate_on_submit():
            try:
                book = create_book(book_form).__dict__
                book["_id"] = ObjectId()
                send_image_to_db(book_form)
                if book_form.picture.data is None:
                    book["picture"] = None
                else:
                    book["picture"] = book_form.picture.data.filename
                db.books.insert_one(book)
                flash("Kniha úspěšně přidána", "success")
            except Exception:
                flash("Chyba při přidávání knihy", "danger")

        if len(list(unverified_users.clone())) != 0:
            flash(f"Počet uživatelů k ověření: {len(list(unverified_users.clone()))}", "warning")

    if search_form.validate_on_submit():
        search_value = search_form.search_data.data
        if not search_value:
            search_value = "None"

    books = books_listing(search_value, sort_value, type)

    borrowed_books, borrowed_until = books_borrowed_by_user(username=current_user.username)

    return render_template('library_catalog.html', books=books, borrowed_books=borrowed_books,
                           book_form=book_form, unverified_users=unverified_users, user=current_user,
                           search_form=search_form, sort_value=sort_value, type=type, search_value=search_value, borrowed_until=borrowed_until )


@app.route('/users_catalog/<sort_value>/<type>/<search_value>', methods=['GET', 'POST'])
@login_required
def users_catalog(sort_value, type, search_value):
    if current_user.role != "Admin":
        abort(403)
    search_form = SearchForm(csrf=False)

    if search_form.validate_on_submit():
        search_value = search_form.search_data.data
        if not search_value:
            search_value = "None"
            print("test")
    users = users_listing(search_value, sort_value, type)

    return render_template("users_catalog.html", users=users, search_form=search_form, search_value=search_value,
                           sort_value=sort_value, type=type)


@app.route('/users_catalog/edit_user/<user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != "Admin":
        abort(403)
    edit_form = EditUser(csrf=False)
    if request.method == 'POST':
        try:
            user = make_user_object(db.users.find_one({"_id": ObjectId(user_id)}))
            user.update(edit_form)
            flash("Úspěšně upraveno", "success")
        except Exception:
            flash("Nepodařilo se upravit", "warning")

    borrowed_books, borrowed_until = books_borrowed_by_user(user_id=user_id)

    user = make_user_object(db.users.find_one({"_id": ObjectId(user_id)}))
    user_history = user.user_history()
    user = vars(user)
    return render_template("edit_user.html", user=user, edit_form=edit_form, borrowed_books=borrowed_books,
                           user_history=user_history, borrowed_until=borrowed_until)


@app.route('/users_catalog/edit_user/give_user_book/<user_id>/<sort_value>/<type>/<search_value>',
           methods=['GET', 'POST'])
@login_required
def give_user_book(user_id, type, sort_value, search_value):
    if current_user.role != "Admin":
        abort(403)
    search_form = SearchForm(csrf=False)

    if search_form.validate_on_submit():
        search_value = search_form.search_data.data
        if not search_value:
            search_value = "None"

    books = books_listing(search_value, sort_value, type)

    user = db.users.find_one({"_id": ObjectId(user_id)})
    return render_template("give_user_book.html", books=books, user=user, search_form=search_form,
                           search_value=search_value, sort_value=sort_value, type=type)


@app.route('/library_catalog/edit_book/<book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if current_user.role != "Admin":
        abort(403)
    edit_book_form = CreateBookForm(csrf=False)
    if request.method == 'POST':
        # try:
            book = make_book_object(db.books.find_one({"_id": ObjectId(book_id)}))
            book.update_book(edit_book_form)
            send_image_to_db(edit_book_form)
            flash("Úspěšně upraveno", "success")
        # except Exception:
        #     flash("Nepodařilo se upravit", "warning")
    book = db.books.find_one({"_id": ObjectId(book_id)})

    borrowed_by_users = users_with_borrowed_book(book_id)

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
        return redirect(url_for('library_catalog', sort_value="default", type="asc", search_value="None"))


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
        return redirect(url_for('library_catalog', sort_value="default", type="asc", search_value="None"))


@app.route('/users_catalog/history', methods=['GET', 'POST'])
@login_required
def transactions_history():
    if current_user.role != "Admin":
        abort(403)
    all_users_history = library_history()

    return render_template("history.html", all_users_history=all_users_history)


@app.route('/library_catalog/verify/<user_id>', methods=['GET', 'POST'])
@login_required
def verify(user_id):
    if current_user.role != "Admin":
        abort(403)
    db.users.update_one({"_id": ObjectId(user_id)},
                        {"$set": {"activated": True}})
    return redirect(url_for('library_catalog', sort_value="default", type="asc", search_value="None"))


@app.route('/library_catalog/delete/<book_id>', methods=['GET', 'POST'])
@login_required
def delete_book(book_id):
    if current_user.role != "Admin":
        abort(403)

    book = make_book_object(db.books.find_one({"_id": ObjectId(book_id)}))
    book.delete_book()

    return redirect(url_for("library_catalog", sort_value="default", type="asc", search_value="None"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/book_picture/<filename>')
def serve_img(filename=None):
    if filename is None or filename == "" or filename =="None":
        filename = "No_Image_Available.jpg"
    img = io.BytesIO(db.images.find_one({"filename": filename})["data"])
    return send_file(img, mimetype="jpeg")


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/users_catalog/delete/<user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    if current_user.role != "Admin":
        abort(403)

    user = make_user_object(db.users.find_one({"_id": ObjectId(user_id)}))
    user.delete_user()

    return redirect(url_for("users_catalog", sort_value="default", type="asc", search_value="None"))

#testing some stuff
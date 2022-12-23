# This file contains the models used in the database. It defines the tables and columns used in the database.
from bson import ObjectId
from flask_login import UserMixin
from flask import flash, request
from datetime import datetime, timedelta

from knihovna_app.config import db
from knihovna_app.forms import EditUser


class User(UserMixin):
    def __init__(self, fname: object, lname: object, birthnum: object, email: object, street: object, city: object,
                 zip: object, username: object, password: object, role="user", borrowed_books=[], favorites=[],
                 activated=False, _id=None) -> object:
        self.fname = fname
        self.lname = lname
        self.birthnum = birthnum
        self.email = email
        self.street = street
        self.city = city
        self.zip = zip
        self.username = username
        self.password = password
        self.role = role
        self.borrowed_books = borrowed_books
        self.favorites = favorites
        self.activated = activated
        self._id = _id

    # UserMixin methods
    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True

    @staticmethod
    def is_anonymous():
        return False

    def get_id(self):
        return self.username

    def get_string_id(self):
        return str(self._id)

    # Basic users methods
    def borrow_book(self, book_id):

        if any(book_id in book["borrowed_book_id"] for book in self.borrowed_books):
            flash("Knihu již máte zapůjčenou.", 'danger')
        elif len(self.borrowed_books) > 5:
            flash("Již máte zapůjčený maximální počet knih.", "danger")
        else:
            db.users.update_one(
                {"username": self.username},
                {"$push": {"borrowed_books": {"borrowed_book_id": book_id, "time_stamp": datetime.today()}}}
            )
            db.books.update_one(
                {"_id": ObjectId(book_id)},
                {"$push": {"borrowed_by": {"user_id": self._id, "until": datetime.today() + timedelta(days=6)}}}
            )
            db.books.update_one(
                {"_id": ObjectId(book_id)},
                {"$inc": {"num_pcs": -1}}
            )

            flash("Kniha úspěšně zapůjčena.", 'success')
    def return_book(self, book_id):
        try:
            db.users.update_one({"username": self.username},
                                {"$pull": {"borrowed_books": {"borrowed_book_id": book_id}}})
            db.books.update_one({"_id": ObjectId(book_id)},
                                {"$pull": {
                                    "borrowed_by": {"user_id": db.users.find_one({"username": self.username})["_id"]}}})
            db.books.update_one({"_id": ObjectId(book_id)},
                                {"$inc": {"num_pcs": 1}})
            flash("Kniha úspěšně vrácena.", 'success')
        except:
            flash("Kniha nemohla být vrácena", "warning")

    # Admin methods
    def delete_book(self, book):
        if self.role == 'Admin':
            Book.delete_book()

    def add_book(self, book):
        if self.role == 'Admin':
            Book.add_book()

    def activate_user(self, user):
        if self.role == 'Admin':
            user.activated = True

    def set_role(self):
        if self.username == "admin":
            self.role = 'Admin'

    def edit_user(self):
        pass


class Book:
    def __init__(self, title, author, release_year, num_pages, num_pcs, picture=None):
        self.title = title
        self.author = author
        self.release_year = release_year
        self.num_pages = num_pages
        self.num_pcs = num_pcs
        self.picture = picture
        self.borrowed_by = []

    def borrow(self, user):
        return

    def return_book(self):
        return

    def add_book(self):
        return

    def delete_book(self):
        return

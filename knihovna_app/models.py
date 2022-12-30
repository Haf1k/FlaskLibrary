# This file contains the models used in the database. It defines the tables and columns used in the database.
from datetime import datetime, timedelta

from bson import ObjectId
from flask import flash
from flask_login import UserMixin

from knihovna_app.config import db


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

        time_of_return = (datetime.today() + timedelta(days=6)).isoformat()

        if any(book_id in str(book["borrowed_book_id"]) for book in self.borrowed_books):
            flash("Knihu již máte zapůjčenou.", 'danger')
        elif len(self.borrowed_books) > 5:
            flash("Již máte zapůjčený maximální počet knih.", "danger")
        else:
            db.users.update_one(
                {"username": self.username},
                {"$push": {"borrowed_books": {"borrowed_book_id": ObjectId(book_id),
                                              "borrowed_until": time_of_return}}}
            )
            db.books.update_one(
                {"_id": ObjectId(book_id)},
                {"$push": {"borrowed_by": {"user_id": self._id, "borrowed_until": time_of_return}}}
            )
            db.books.update_one(
                {"_id": ObjectId(book_id)},
                {"$inc": {"num_pcs": -1}}
            )

            db.auditLog.insert_one({"user_id": self._id,
                                    "book_id": ObjectId(book_id),
                                    "type_of_transaction": "borrow",
                                    "timestamp": datetime.today().isoformat()
                                    })

            flash("Kniha úspěšně zapůjčena.", 'success')

    def return_book(self, book_id):
        try:

            db.users.update_one({"username": self.username},
                                {"$pull": {"borrowed_books": {"borrowed_book_id": ObjectId(book_id)}}})
            db.books.update_one({"_id": ObjectId(book_id)},
                                {"$pull": {
                                    "borrowed_by": {"user_id": db.users.find_one({"username": self.username})["_id"]}}})
            db.books.update_one({"_id": ObjectId(book_id)},
                                {"$inc": {"num_pcs": 1}})
            db.auditLog.insert_one({"user_id": self._id,
                                    "book_id": ObjectId(book_id),
                                    "type_of_transaction": "return",
                                    "timestamp": datetime.today().isoformat()
                                    })
            flash("Kniha úspěšně vrácena.", 'success')
        except Exception:
            flash("Kniha nemohla být vrácena", "warning")

    # Admin methods

    def delete_user(self):
        if db.users.find_one({"_id": ObjectId(self._id)})["borrowed_books"]:
            flash("Uživatel nemůže být smazán, jelikož má stále zapůjčené knihy.", 'danger')
        else:
            db.users.delete_one({"_id": ObjectId(self._id)})
            flash("Uživatel byl úspěšně smazán", "success")

    def update(self, edit_form):
        db.users.update_one({"_id": self._id},
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

    def user_history(self):

        output = []
        logs = db.auditLog.find({"user_id": (self._id)})

        for log in logs:
            book = db.books.find_one({"_id": log["book_id"]})
            match log["type_of_transaction"]:
                case "borrow":
                    transaction = "Zapůjčení"
                case "return":
                    transaction = "Navrácení"
                case "automatic return":
                    transaction = "Vypršení lhůty zapůjčení"
                case _:
                    return

            value = {"title": book["title"],
                     "author": book["author"],
                     "release_year": book["release_year"],
                     "transaction": transaction,
                     "date": datetime.fromisoformat(log["timestamp"].replace("Z", ''))}
            output.append(value)

        return output[::-1]


class Book:
    def __init__(self, title, author, release_year, num_pages, num_pcs, borrowed_by=[], picture=None, _id=None):
        self.title = title
        self.author = author
        self.release_year = release_year
        self.num_pages = num_pages
        self.num_pcs = num_pcs
        self.picture = picture
        self.borrowed_by = borrowed_by
        self._id = _id

    def borrow(self, user):
        return

    def update_book(self, edit_book_form):
        db.books.update_one({"_id": ObjectId(self._id)},
                            {"$set": {"title": edit_book_form.title.data,
                                      "author": edit_book_form.author.data,
                                      "release_year": str(edit_book_form.release_year.data),
                                      "num_pages": edit_book_form.num_pages.data,
                                      "num_pcs": edit_book_form.num_pcs.data,
                                      "picture": edit_book_form.picture.data
                                      }})

    def return_book(self):
        return

    def add_book(self):
        return

    def delete_book(self):
        if db.books.find_one({"_id": ObjectId(self._id)})["borrowed_by"]:
            flash("Knihu nelze smazat, jelikož ji má někdo půjčenou.", 'danger')
        else:
            db.books.delete_one({"_id": ObjectId(self._id)})
            flash("Kniha byla úspěšně smazána", "success")
        return

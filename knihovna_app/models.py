# This file contains the models used in the database. It defines the tables and columns used in the database.
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, fname: object, lname: object, birthnum: object, email: object, street: object, city: object,
                 zip: object, username: object, password: object, role=None, borrowed_books=[], favorites=[],
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

    # Basic users methods
    def borrow_book(self, book):
        self.borrowed_books.append(book)

    def return_book(self, book):
        self.borrowed_books.remove(book)

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


class Book:
    def __init__(self, title, author, release_year, num_pages, num_pcs, picture=None, available=True):
        self.title = title
        self.author = author
        self.release_year = release_year
        self.num_pages = num_pages
        self.num_pcs = num_pcs
        self.picture = picture
        self.available = available
        self.borrowed_by = []

    def borrow(self, user):
        return

    def return_book(self):
        return

    def add_book(self):
        return

    def delete_book(self):
        return

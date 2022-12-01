# This file contains the models used in the database. It defines the tables and columns used in the database.


class User:
    def __init__(self, fname: object, lname: object, birthnum: object, email: object, street: object, city: object,
                 zip: object, username: object, password: object) -> object:
        self.fname = fname
        self.lname = lname
        self.birthnum = birthnum
        self.email = email
        self.street = street
        self.city = city
        self.zip = zip
        self.username = username
        self.password = password
        self.role = None
        self.borrowed_books = []
        self.favorites = []
        self.activated = False

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
    def __init__(self, title, author, release_year, num_pages, num_pcs, picture):
        self.title = title
        self.author = author
        self.release_year = release_year
        self.num_pages = num_pages
        self.num_pcs = num_pcs
        self.picture = picture
        self.available = False
        self.borrowed_by = []

    def borrow(self, user):
        return

    def return_book(self):
        return

    def add_book(self):
        return

    def delete_book(self):
        return

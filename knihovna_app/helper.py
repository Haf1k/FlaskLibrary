import io
from datetime import datetime

from PIL import Image
from bson import ObjectId
from knihovna_app.config import db
from models import User, Book


def make_user_object(user: dict):
    user_object = User(fname=user['fname'],
                       lname=user['lname'],
                       birthnum=user['birthnum'],
                       email=user['email'],
                       street=user['street'],
                       city=user['city'],
                       zip=user['zip'],
                       username=user['username'],
                       password=user['password'],
                       role=user['role'],
                       borrowed_books=user['borrowed_books'],
                       favorites=user['favorites'],
                       activated=user['activated'],
                       _id=user['_id'])
    return user_object


def make_book_object(book: dict):
    book_object = Book(
        title=book['title'],
        author=book['author'],
        release_year=book['release_year'],
        num_pages=book['num_pages'],
        num_pcs=book['num_pcs'],
        picture=book['picture'],
        borrowed_by=book['borrowed_by'],
        _id=book['_id'])

    return book_object


def create_book(book_form):
    return Book(title=book_form.title.data,
                author=book_form.author.data,
                release_year=str(book_form.release_year.data),
                num_pages=book_form.num_pages.data,
                num_pcs=book_form.num_pcs.data,
                picture=book_form.picture.data)


def create_user(form, hash_password):
    return User(fname=form.fname.data,
                lname=form.lname.data,
                birthnum=str(form.birthnum.data),
                email=form.email.data,
                street=form.street.data,
                city=form.city.data,
                zip=form.zip.data,
                username=form.username.data,
                password=hash_password)


def books_listing(search_data=None, sort_value="author", type=1):
    if type == "asc":
        type = 1
    else:
        type = -1

    if search_data != "None" and search_data is not None:
        books = db.books.aggregate([
            {
                "$match": {
                    "$or": [{"author": {"$regex": ".*" + search_data + ".*", "$options": "i"}},
                            {"title": {"$regex": ".*" + search_data + ".*", "$options": "i"}},
                            {"release_year": {"$regex": ".*" + search_data + ".*", "$options": "i"}}]
                }
            },
            {
                "$sort": {sort_value: type}
            }
        ])

    else:
        books = db.books.find({}).sort(sort_value, type)

    return books


def books_borrowed_by_user(username=None, user_id=None):
    if username:
        borrowed_books = db.users.find_one({"username": username})["borrowed_books"]
    elif user_id:
        borrowed_books = db.users.find_one({"_id": ObjectId(user_id)})["borrowed_books"]
    else:
        return
    return [db.books.find_one({"_id": ObjectId(each["borrowed_book_id"])}) for each in borrowed_books]


def users_with_borrowed_book(book_id=None):
    borrowed_by_users = db.books.find_one({"_id": ObjectId(book_id)})["borrowed_by"]
    return [db.users.find_one({"_id": ObjectId(each["user_id"])}) for each in borrowed_by_users]


def users_listing(search_data=None, sort_value="author", type=1):
    if type == "asc":
        type = 1
    else:
        type = -1
    if search_data not in ("None", "none") and search_data is not None:
        return db.users.aggregate([
            {
                "$match": {
                    "$or": [{"lname": {"$regex": ".*" + search_data + ".*", "$options": "i"}},
                            {"fname": {"$regex": ".*" + search_data + ".*", "$options": "i"}},
                            {"city": {"$regex": ".*" + search_data + ".*", "$options": "i"}},
                            {"street": {"$regex": ".*" + search_data + ".*", "$options": "i"}},
                            {"birthnum": {"$regex": ".*" + search_data + ".*", "$options": "i"}}]
                }
            },
            {
                "$sort": {sort_value: type}
            }
        ])
    else:
        return db.users.find({"role": "user"}).sort(sort_value, type)


def library_history():
    output = []
    logs = db.auditLog.find()

    for log in logs:
        book = db.books.find_one({"_id": log["book_id"]})
        user = db.users.find_one({"_id": log["user_id"]})

        match log["type_of_transaction"]:
            case "borrow":
                transaction = "Zapůjčení"
            case "return":
                transaction = "Navrácení"
            case "automatic return":
                transaction = "Vypršení lhůty zapůjčení"
            case _:
                return

        value = {"fname": user["fname"],
                 "lname": user["lname"],
                 "username": user["username"],
                 "title": book["title"],
                 "author": book["author"],
                 "release_year": book["release_year"],
                 "transaction": transaction,
                 "date": datetime.fromisoformat(log["timestamp"].replace("Z", ''))}
        output.append(value)

    return output[::-1]


def send_image_to_db(book_form):
    if book_form.picture.data is None:
        return
    image = Image.open(book_form.picture.data)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format='JPEG')
    image_to_database = {"_id": ObjectId(),
                         "filename": book_form.picture.data.filename,
                         "data": image_bytes.getvalue()}
    db.images.insert_one(image_to_database)

    return

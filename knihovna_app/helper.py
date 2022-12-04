from models import User


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

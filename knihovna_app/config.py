# This file contains all the configuration settings used by the application.

from flask_pymongo import pymongo

# setup mongodb
secret = "45117112c27cd80ecbf597ff2fc2fc3e6fa80060"
cluster = pymongo.MongoClient(
    "mongodb+srv://aplknihovnice:S18HreOHOFbZ0Gac@knihovnadb.cwbkq6y.mongodb.net/?retryWrites=true&w=majority")
db = cluster['knihovnadb']

db.users.create_index('email', unique=True)
db.users.create_index('username', unique=True)
db.users.create_index('birthnum', unique=True)
db.images.create_index('filename', unique=True)

db.books.create_index([('title', 'text'), ('author', 'text'), ('release_year', 'text')])
db.users.create_index(
    [('fname', 'text'), ('lname', 'text'), ('birthnum', 'text'), ('street', 'text'), ('city', 'text'), ('zip', 'text')])

# db.users.create_index('borrowed_books.time_stamp', expireAfterSeconds=60) # is deleting whole user

# testtest
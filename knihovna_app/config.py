# This file contains all of the configuration settings used by the application.

import pymongo

# setup mongodb
secret = "45117112c27cd80ecbf597ff2fc2fc3e6fa80060"
cluster = pymongo.MongoClient(
    "mongodb+srv://aplknihovnice:S18HreOHOFbZ0Gac@knihovnadb.cwbkq6y.mongodb.net/?retryWrites=true&w=majority")
db = cluster['knihovnadb']

db.users.create_index('email', unique=True)
db.users.create_index('username', unique=True)
db.users.create_index('birthnum', unique=True)




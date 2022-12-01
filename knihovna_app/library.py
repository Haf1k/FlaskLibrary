# This file contains the logic for the application. It defines the routes, view functions, and other operations.
import bcrypt
from knihovna_app.models import User
from knihovna_app.config import db


# create default admin
def create_admin():
    admin_exist = db.users.find_one({'username': "admin"})
    if admin_exist is None:
        password = 'admin'
        psw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        admin = User('None',
                    'None',
                    'None',
                    'None',
                    'None',
                    'None',
                    'None',
                    'admin',
                    psw)
        admin.set_role()
        admin.activate_user(admin)
        db.users.insert_one(admin.__dict__)



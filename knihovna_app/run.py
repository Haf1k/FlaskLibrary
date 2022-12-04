from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
csrf = CSRFProtect(app)
app.config['SECRET_KEY'] = 'SECRETKEY'

if __name__ == '__main__':
    app.debug = True
    import logging
    logging.basicConfig(filename='error.log', level=logging.DEBUG)
    app.run(host="0.0.0.0")

import routes, models
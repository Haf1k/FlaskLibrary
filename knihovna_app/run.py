from flask import Flask
from flask_login import LoginManager

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

if __name__ == '__main__':
    app.debug = True
    import logging
    logging.basicConfig(filename='error.log', level=logging.DEBUG)
    app.run(host="0.0.0.0")

import routes, models
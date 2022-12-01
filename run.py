from knihovna_app import *


if __name__ == '__main__':
    app.debug = True
    import logging
    logging.basicConfig(filename='error.log', level=logging.DEBUG)
    app.run(host="0.0.0.0")

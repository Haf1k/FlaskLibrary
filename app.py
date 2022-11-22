from flask import Flask, render_template, url_for, request, session, redirect
from flask_pymongo import PyMongo
import bcrypt

app = Flask(__name__)

app = Flask(__name__)
app.config["SECRET_KEY"] = "45117112c27cd80ecbf597ff2fc2fc3e6fa80060"
app.config["MONGO_URI"] = "mongodb+srv://apl_knihovnice:iVl84wy7N9mQfPf0@cluster0.7m5pmxe.mongodb.net/?retryWrites" \
                          "=true&w=majority "
# setup mongodb
mongodb_client = PyMongo(app)
db = mongodb_client.db


@app.route('/')
def home():
    if 'username' in session:
        return 'Jste přihlášen jako ' + session['username']

    return render_template('main.html')

@app.route('/login', methods=['POST','GET'])
def login():
    return render_template('login.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if request.method == 'POST':
        users = db.users
        userExist = users.find_one({'name' : request.form['username']})

        if userExist is None:
            hashPassword = bcrypt.hashpw(request.form['password'].encode('utf-8'), bcrypt.gensalt())
            db.users.insert_one({'name' : request.form['username'], 'password' : hashPassword})
            session['username'] = request.form['username']
            return redirect(url_for('main'))
        return 'Nejde to. Uzivatel jiz existuje.'
    return render_template('register.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)


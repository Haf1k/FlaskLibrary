from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from models import User


class RegistrationForm(FlaskForm):
    fname = StringField('Jméno', validators=[DataRequired()])
    lname = StringField('Příjmení', validators=[DataRequired()])
    birthnum = StringField('Rodné čislo bez /', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    street = StringField('Ulice', validators=[DataRequired()])
    city = StringField('Město', validators=[DataRequired()])
    zip = StringField('PSČ', validators=[DataRequired()])
    username = StringField('Uživatelské jméno', validators=[DataRequired()])
    password = StringField('Heslo', validators=[DataRequired()])
    password2 = PasswordField('Zopakujte heslo',
                              validators=[DataRequired, EqualTo('password', message='Hesla se musi shodovat')])
    submit = SubmitField('Registruj se')

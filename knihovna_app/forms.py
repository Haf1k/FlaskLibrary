from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from models import User


class RegistrationForm(FlaskForm):
    fname = StringField('Jméno', validators=[DataRequired(), Length(max=20)])
    lname = StringField('Příjmení', validators=[DataRequired(), Length(max=20)])
    birthnum = StringField('Rodné dasdasdčislo bez /', validators=[DataRequired(), Length(min=8, max=10)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=20)])
    street = StringField('Ulice', validators=[DataRequired(), Length(max=20)])
    city = StringField('Město', validators=[DataRequired(), Length(max=20)])
    zip = StringField('PSČ', validators=[DataRequired(), Length(max=20)])
    username = StringField('Uživatelské jméno', validators=[DataRequired(), Length(max=20)])
    password = PasswordField('Heslo', validators=[DataRequired()])
    password2 = PasswordField('Zopakujte heslo',
                              validators=[DataRequired(), EqualTo('password', message='Hesla se musi shodovat')])
    submit = SubmitField('Registruj se')

class LoginForm(FlaskForm):
    username = StringField('Uživatelské jméno', validators=[DataRequired()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    submit = SubmitField('Přihlásit')

from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FileField, BooleanField, DateField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, NumberRange
from models import User


class RegistrationForm(FlaskForm):
    fname = StringField('Jméno', validators=[DataRequired(), Length(max=30)])
    lname = StringField('Příjmení', validators=[DataRequired(), Length(max=30)])
    birthnum = StringField('Rodné dasdasdčislo bez /', validators=[DataRequired(), Length(min=8, max=10)])
    email = StringField('E-mail', validators=[DataRequired(), Email(), Length(max=30)])
    street = StringField('Ulice', validators=[DataRequired(), Length(max=30)])
    city = StringField('Město', validators=[DataRequired(), Length(max=30)])
    zip = StringField('PSČ', validators=[DataRequired(), Length(max=30)])
    username = StringField('Uživatelské jméno', validators=[DataRequired(), Length(max=30)])
    password = PasswordField('Heslo', validators=[DataRequired()])
    password2 = PasswordField('Zopakujte heslo',
                              validators=[DataRequired(), EqualTo('password', message='Hesla se musi shodovat')])
    submit = SubmitField('Registruj se')


class LoginForm(FlaskForm):
    username = StringField('Uživatelské jméno', validators=[DataRequired()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    submit = SubmitField('Přihlásit')


class CreateBookForm(FlaskForm):
    title = StringField('Název knihy', validators=[DataRequired()])
    author = StringField('Jméno autora', validators=[DataRequired(), Length(max=30)])
    release_year = IntegerField('Rok vydání',
                                validators=[DataRequired(), NumberRange(max=date.today().year, message="Zadejte platný rok")])
    num_pages = IntegerField('Počet stran',
                             validators=[DataRequired(),
                                         NumberRange(min=0, max=9999, message="Zadejte platný počet stran")])
    num_pcs = IntegerField('Počet výtisků v knihovně',
                           validators=[DataRequired(),
                                       NumberRange(min=0, max=9999, message="Zadejte platný počet výtisků")])
    picture = FileField("Obrázek titulní strany")
    available = BooleanField("Umožnit zapůjčení", validators=[DataRequired()])
    submit = SubmitField('Uložit')

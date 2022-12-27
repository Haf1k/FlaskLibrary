from datetime import date

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, FileField, BooleanField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange


class RegistrationForm(FlaskForm):
    fname = StringField('Jméno', validators=[DataRequired(), Length(max=30)])
    lname = StringField('Příjmení', validators=[DataRequired(), Length(max=30)])
    birthnum = IntegerField('Rodné čislo bez /', validators=[DataRequired(), NumberRange(min=1000000, max=9999999999)])
    email = EmailField('E-mail', validators=[DataRequired(), Email(message="Zadejte platný email."), Length(max=30)])
    street = StringField('Ulice', validators=[DataRequired(), Length(max=30)])
    city = StringField('Město', validators=[DataRequired(), Length(max=30)])
    zip = IntegerField('PSČ', validators=[DataRequired()])
    username = StringField('Uživatelské jméno', validators=[DataRequired(), Length(max=30)])
    password = PasswordField('Heslo', validators=[DataRequired()])
    password2 = PasswordField('Zopakujte heslo',
                              validators=[DataRequired(), EqualTo('password', message='Hesla se musi shodovat')])
    submit = SubmitField('Registruj se')


class EditUser(FlaskForm):
    fname = StringField('Jméno', validators=[DataRequired(), Length(max=30)])
    lname = StringField('Příjmení', validators=[DataRequired(), Length(max=30)])
    birthnum = IntegerField('Rodné čislo bez /', validators=[DataRequired(), NumberRange(min=1000000, max=9999999999)])
    email = EmailField('E-mail', validators=[DataRequired(), Email(message="Zadejte platný email."), Length(max=30)])
    street = StringField('Ulice', validators=[DataRequired(), Length(max=30)])
    city = StringField('Město', validators=[DataRequired(), Length(max=30)])
    zip = IntegerField('PSČ', validators=[DataRequired(), Length(max=30)])
    username = StringField('Uživatelské jméno', validators=[DataRequired(), Length(max=30)])
    activated = BooleanField('Aktivace účtu')
    role = StringField('Role v knihovně', default='user')
    submit = SubmitField('Uložit')


class LoginForm(FlaskForm):
    username = StringField('Uživatelské jméno', validators=[DataRequired()])
    password = PasswordField('Heslo', validators=[DataRequired()])
    submit = SubmitField('Přihlásit')


class CreateBookForm(FlaskForm):
    title = StringField('Název knihy', validators=[DataRequired()])
    author = StringField('Jméno autora', validators=[DataRequired(), Length(max=30)])
    release_year = IntegerField('Rok vydání',
                                validators=[DataRequired(),
                                            NumberRange(max=date.today().year, message="Zadejte platný rok")])
    num_pages = IntegerField('Počet stran',
                             validators=[DataRequired(),
                                         NumberRange(min=0, max=9999, message="Zadejte platný počet stran")])
    num_pcs = IntegerField('Počet výtisků v knihovně',
                           validators=[DataRequired(),
                                       NumberRange(min=0, max=9999, message="Zadejte platný počet výtisků")])
    picture = FileField("Obrázek titulní strany")
    submit = SubmitField('Uložit')


class SearchForm(FlaskForm):
    search_data = StringField("Hledat", validators=[Length(min=3)])
    submit = SubmitField('Hledat')

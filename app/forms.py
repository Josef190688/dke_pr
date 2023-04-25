from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired, Optional, InputRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('merken')
    submit = SubmitField('Login')

class CreatePersonForm(FlaskForm):
    username = StringField('Benutzername', validators=[InputRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    firstname = StringField('Vorname', validators=[DataRequired()])
    lastname = StringField('Nachname', validators=[DataRequired()])
    birthdate = DateField('Geburtsdatum', format='%Y-%m-%d', validators=[Optional()])
    phone_number = StringField('Telefonnummer', validators=[Optional()])
    profession = StringField('Beruf', validators=[Optional()])
    is_admin = BooleanField('Admin', validators=[Optional()])
    submit = SubmitField('erstellen')
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Optional, InputRequired
from wtforms import ValidationError
from app import models

class UniqueUsername(object):
    def __init__(self, message=None):
        if not message:
            message = 'Benutzername bereits vergeben.'
        self.message = message

    def __call__(self, form, field):
        # Überprüfe, ob der Benutzername bereits in der Datenbank existiert
        existing_user = models.Person.query.filter_by(username=field.data).first()
        if existing_user:
            raise ValidationError(self.message)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    remember_me = BooleanField('merken')
    submit = SubmitField('Login')

class CreatePersonForm(FlaskForm):
    username = StringField('Benutzername', validators=[InputRequired(), UniqueUsername()])
    password = PasswordField('Passwort', validators=[DataRequired()])
    firstname = StringField('Vorname', validators=[DataRequired()])
    lastname = StringField('Nachname', validators=[DataRequired()])
    birthdate = DateField('Geburtsdatum', format='%Y-%m-%d', validators=[Optional()])
    phone_number = StringField('Telefonnummer', validators=[Optional()])
    profession = StringField('Beruf', validators=[Optional()])
    is_admin = BooleanField('Admin', validators=[Optional()])
    submit = SubmitField('erstellen')

class UpdatePersonForm(FlaskForm):
    id = StringField('id', render_kw={"readonly": True})
    username = StringField('Benutzername', validators=[InputRequired(), UniqueUsername()])
    password = PasswordField('Passwort', render_kw={'placeholder': 'Lassen Sie dieses Feld leer, um das Passwort unverändert zu lassen'})
    firstname = StringField('Vorname', validators=[DataRequired()])
    lastname = StringField('Nachname', validators=[DataRequired()])
    birthdate = DateField('Geburtsdatum', format='%Y-%m-%d', validators=[Optional()])
    phone_number = StringField('Telefonnummer', validators=[Optional()])
    profession = StringField('Beruf', validators=[Optional()])
    is_admin = BooleanField('Admin', validators=[Optional()])
    submit = SubmitField('aktualisieren')

class WertpapiereKaufenForm(FlaskForm):
    selectedWertpapierId = HiddenField('Wertpapier')
    selectedBoersenId = HiddenField()
    comp_id = HiddenField()
    amount = IntegerField('Anzahl', render_kw={'class': 'form-control', 'id': 'amountInput'})
    depot_id = HiddenField()
    price = HiddenField()
    currency = HiddenField()
    total_to_pay = HiddenField()
    submit = SubmitField('kaufen')
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# DB STRUCTURE
# ------------------------------------------------------------------------------------------

class Account(db.Model):
    __tablename__ = 'account'

    account_id = db.Column(db.Integer, primary_key=True)
    account_balance_in_euro = db.Column(db.Float, nullable=False, default=0.0)
    displayed_currency = db.Column(db.Enum('EUR', 'USD'), nullable=False, default='EUR')

class Person(UserMixin, db.Model):
    __tablename__ = 'person'

    person_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.DateTime)
    phone_number = db.Column(db.String(255))
    profession = db.Column(db.String(255))
    is_admin = db.Column(db.Boolean, nullable=False)
    persons_account_id = db.Column(db.Integer, db.ForeignKey('account.account_id'), nullable=False, unique=True)

    account = db.relationship('Account', backref='persons')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        return str(self.person_id)

@login.user_loader
def load_user(id):
    return Person.query.get(int(id))
    
class Deposit(db.Model):
    __tablename__ = 'deposit'

    deposit_id = db.Column(db.Integer, primary_key=True)
    deposit_name = db.Column(db.String(255), nullable=False, unique=True)
    deposits_person_id = db.Column(db.Integer, db.ForeignKey('person.person_id'), nullable=False, unique=True)

    person = db.relationship('Person', backref='deposits')

class SecuritiesPosition(db.Model):
    __tablename__ = 'securities_position'

    securities_position_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    market_id = db.Column(db.Integer, nullable=False)
    purchase_timestamp = db.Column(db.DateTime, nullable=False)
    positions_deposit_id = db.Column(db.Integer, db.ForeignKey('deposit.deposit_id'), nullable=False)

    deposit = db.relationship('Deposit', backref='securities_positions')

# CRUD Personenverwaltung
# ------------------------------------------------------------------------------------------
# CREATE
def create_person(username, password, first_name, last_name, birth_date, phone_number, profession, is_admin):
    try:
        account = Account()
        db.session.add(account)
        person = Person(username=username, first_name=first_name, last_name=last_name, birth_date=birth_date, phone_number=phone_number, profession=profession, is_admin=is_admin, account=account)
        person.set_password(password)
        db.session.add(person)
        db.session.commit()
        return person
    except Exception as error:
        db.session.rollback()

# READ
def get_person(person_id):
    return Person.query.filter_by(person_id=person_id).first()

def get_persons_by_filter(filter):
    return Person.query.filter(
        (Person.username.ilike(f"%{filter}%")) |
        (Person.first_name.ilike(f"%{filter}%")) |
        (Person.last_name.ilike(f"%{filter}%"))
    ).all()

def get_all_persons():
    return Person.query.all()

# UPDATE
def update_person(person_id, username=None, password=None, first_name=None, last_name=None, birth_date=None, phone_number=None, profession=None, is_admin=None):
    person = get_person(person_id)
    if not person:
        return None
    if username:
        person.username = username
    if password:
        person.set_password(password)
    if first_name:
        person.first_name = first_name
    if last_name:
        person.last_name = last_name
    if birth_date:
        person.birth_date = birth_date
    if phone_number:
        person.phone_number = phone_number
    if profession:
        person.profession = profession
    if is_admin is not None:
        person.is_admin = is_admin
    db.session.commit()
    return person

# DELETE
def delete_person(person_id):
    try:
        person = get_person(person_id)
        if not person:
            return False
        db.session.delete(person)
        db.session.commit()
        return True
    except:
        return False

#TODO: CRUD Depotübersicht
# ------------------------------------------------------------------------------------------
# CREATE
def create_deposit(deposit_name, person_id):
    try:
        deposit = Deposit(deposit_name=deposit_name, deposits_person_id=person_id)
        db.session.add(deposit)
        db.session.commit()
        return deposit
    except:
        db.session.rollback()
        return None
    
# READ


#TODO: CRUD Depotpositionen
# ------------------------------------------------------------------------------------------

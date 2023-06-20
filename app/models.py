from typing import Union

import requests
from app import db, login, converter
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

# DB STRUCTURE
# ------------------------------------------------------------------------------------------

class Account(db.Model):
    __tablename__ = 'account'

    account_id = db.Column(db.Integer, primary_key=True)
    account_balance_in_euro = db.Column(db.Float, nullable=False, default=0.0)
    displayed_currency = db.Column(db.Enum('EUR', 'USD'), nullable=False, default='EUR')

    def __str__(self):
        return f'{self.displayed_currency} {self.format_account_balance()}'

    def format_account_balance(self):
        return f'{self.account_balance_in_euro:.2f}'.replace('.', ',')
    
    def update(self, displayed_currency=None, account_balance_in_euro=None):
        if displayed_currency is not None:
            self.displayed_currency = displayed_currency
        if account_balance_in_euro is not None:
            self.account_balance_in_euro = account_balance_in_euro
        db.session.commit()

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

    def to_dict(self):
        return {
            'deposit_id': self.deposit_id,
            'deposit_name': self.deposit_name,
            'deposits_person_id': self.deposits_person_id
        }

class SecuritiesPosition(db.Model):
    __tablename__ = 'securities_position'

    securities_position_id = db.Column(db.Integer, primary_key=True)
    security_id = db.Column(db.Integer, nullable=False)
    company_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    market_id = db.Column(db.Integer, nullable=False)
    purchase_timestamp = db.Column(db.DateTime, nullable=False)
    positions_deposit_id = db.Column(db.Integer, db.ForeignKey('deposit.deposit_id'), nullable=False)

    deposit = db.relationship('Deposit', backref='securities_positions')

    def get_price(self):
        price = 0.0
        response = requests.get(f'http://localhost:50051/firmen/wertpapiere/{self.security_id}', headers={'Content-Type': 'application/json'})
        security_price = None
        if response.status_code == 200:
            security = response.json()
            security_price = security['price']
            security_currency = security['currency']
            response = requests.get(f'http://localhost:50052/markets/{self.market_id}', headers={'Accept': 'application/json'})
            if response.status_code == 200:
                market = response.json()
                market_currency = market['market_currency_code']
                price = converter.convert(security_price * self.amount, security_currency, market_currency)
        return price
    
    def to_dict(self):
        return {
            'securities_position_id': self.securities_position_id,
            'security_id': self.security_id,
            'company_id': self.company_id,
            'amount': self.amount,
            'market_id': self.market_id,
            'purchase_timestamp': self.purchase_timestamp.isoformat(),
            'positions_deposit_id': self.positions_deposit_id
        }

# CRUD Personenverwaltung
# ------------------------------------------------------------------------------------------
# CREATE
def create_person(username, password, first_name, last_name, birth_date='', phone_number='', profession='', is_admin=False):
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
def get_person(person_id) -> Union[Person, None]:
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

# CRUD Depotübersicht
# ------------------------------------------------------------------------------------------
# CREATE
def create_deposit(person_id, deposit_name):
    try:
        deposit = Deposit(deposit_name=deposit_name, deposits_person_id=person_id)
        db.session.add(deposit)
        db.session.commit()
        return deposit
    except Exception as e:
        print(e)
        db.session.rollback()
        return None
    
# READ
def get_deposit(deposit_id: int) -> Union[Deposit, None]:
    return Deposit.query.filter_by(deposit_id=deposit_id).first()

# DELETE
def delete_deposit(deposit_id):
    try:
        deposit = get_deposit(deposit_id)
        if not deposit:
            return False
        db.session.delete(deposit)
        db.session.commit()
        return True
    except:
        return False

# CRUD Depotpositionen
# ------------------------------------------------------------------------------------------

# CREATE
def create_securities_position(security_id, company_id, amount, market_id, purchase_timestamp, deposit_id):
    try:
        securities_position = SecuritiesPosition(security_id=security_id, company_id=company_id, amount=amount, market_id=market_id, purchase_timestamp=purchase_timestamp, positions_deposit_id=deposit_id)
        db.session.add(securities_position)
        db.session.commit()
        return securities_position
    except Exception as e:
        print(e)
        db.session.rollback()
        return None
    
# READ
def get_securities_positions_by_deposit(deposit_id: int):
    return SecuritiesPosition.query.filter_by(positions_deposit_id=deposit_id).all()

def get_securities_position(securities_position_id: int) -> Union[SecuritiesPosition, None]:
    return SecuritiesPosition.query.get(securities_position_id)

# DELETE
def delete_securities_position(securities_position_id):
    try:
        securities_position = SecuritiesPosition.query.get(securities_position_id)
        if not securities_position:
            return False
        db.session.delete(securities_position)
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False

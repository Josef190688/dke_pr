from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class Account(db.Model):
    __tablename__ = 'account'

    account_id = db.Column(db.Integer, primary_key=True)
    account_balance_in_euro = db.Column(db.Float, nullable=False, default=0)
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

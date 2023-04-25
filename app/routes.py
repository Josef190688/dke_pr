from flask import flash, redirect, render_template, url_for
from app import app, models, db
from app.forms import CreatePersonForm, LoginForm
from flask_login import current_user, login_required, login_user, logout_user

def create_user(username, password, first_name, last_name, birth_date=None, phone_number=None, profession=None, is_admin=False, account_balance_in_euro=0.0, displayed_currency="EUR"):
    try:
        account = models.Account(account_balance_in_euro=account_balance_in_euro, displayed_currency=displayed_currency)
        db.session.add(account)
        person = models.Person(username=username, first_name=first_name, last_name=last_name, birth_date=birth_date, phone_number=phone_number, profession=profession, is_admin=is_admin, account=account)
        person.set_password(password)
        db.session.add(person)
        db.session.commit()
        return person
    except:
        db.session.rollback()

@app.route('/')
@app.route('/index')
@login_required
def index():
    user = {'username': 'Miguel'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        create_user(
            username="admin",
            password="123",
            first_name="Josef",
            last_name="Landmann",
            is_admin=True
        )
        create_user(
            username="max",
            password="123",
            first_name="Max",
            last_name="Mustermann",
            birth_date="1980-01-01",
            phone_number="+49123456789",
            profession="Software Engineer",
            is_admin=False,
            account_balance_in_euro=5000.0,
            displayed_currency="EUR"
        )
    except:
        print("create user failed")
        
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = models.Person.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/person_erstellen', methods=['GET', 'POST'])
@login_required
def person_erstellen():
    form = CreatePersonForm()
    if form.validate_on_submit():
        try:
            create_user(form.username.data,
                        form.password.data,
                        form.firstname.data,
                        form.lastname.data,
                        form.birthdate.data,
                        form.phone_number.data,
                        form.profession.data,
                        form.is_admin.data)
            flash(form.firstname.data + " " + form.lastname.data + " erfolgreich erstellt")
            return redirect(url_for('index'))
        except:
            flash("Person erstellen nicht erfolgreich")
            return redirect(url_for('person_erstellen'))
    return render_template('person_erstellen.html', title='Person erstellen', form=form)
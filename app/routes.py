from flask import flash, make_response, redirect, render_template, url_for
from app import app, models, db
from app.forms import CreatePersonForm, LoginForm
from flask_login import current_user, login_required, login_user, logout_user

@app.route('/')
@app.route('/index', methods=['GET', 'POST', 'DELETE'])
@login_required
def index():
    if current_user.is_admin:
        persons = models.get_all_persons()
        return render_template('index.html', title='Home', persons=persons)
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
    # try:
    #     models.create_user(
    #         username="admin",
    #         password="123",
    #         first_name="Josef",
    #         last_name="Landmann",
    #         is_admin=True
    #     )
    #     models.create_user(
    #         username="max",
    #         password="123",
    #         first_name="Max",
    #         last_name="Mustermann",
    #         birth_date="1980-01-01",
    #         phone_number="+49123456789",
    #         profession="Software Engineer",
    #         is_admin=False,
    #         account_balance_in_euro=5000.0,
    #         displayed_currency="EUR"
    #     )
    # except:
    #     print("create user failed")
        
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
            models.create_person(form.username.data,
                                 form.password.data,
                                 form.firstname.data,
                                 form.lastname.data,
                                 form.birthdate.data,
                                 form.phone_number.data,
                                 form.profession.data,
                                 form.is_admin.data)
            flash(form.firstname.data + " " + form.lastname.data + " erfolgreich erstellt")
            return redirect(url_for('index'))
        except Exception as error:
            flash("Person erstellen nicht erfolgreich")
            return redirect(url_for('person_erstellen'))
    return render_template('person_erstellen.html', title='Person erstellen', form=form)

@app.route('/persons/<int:id>', methods=['DELETE'])
@login_required
def delete_person(id):
    if current_user.is_admin:
        try:
            models.delete_person(id)
            flash("Person erfolgreich gelöscht")
            return make_response('', 204)
        except:
            flash("Person löschen nicht erfolgreich")
    return redirect(url_for('index'))

@app.route('/personen_einfuegen', methods=['GET'])
@login_required
def personen_einfuegen():
    try:
        # Erstelle 10 Test-Personen
        for i in range(1, 11):
            username = f'username{i}'
            password = f'password{i}'
            first_name = f'First{i}'
            last_name = f'Last{i}'
            birth_date = '1990-01-01'
            phone_number = '123456789'
            profession = 'Profession'
            is_admin = False
            models.create_person(username, password, first_name, last_name, birth_date, phone_number, profession, is_admin)
        
        flash("Test-Personen erfolgreich erstellt")
    except:
        flash("Fehler beim Erstellen der Test-Personen")
    
    return redirect(url_for('index'))
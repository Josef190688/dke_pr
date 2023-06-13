from flask import flash, make_response, redirect, render_template, request, url_for
from app import app, models, db
from app.forms import CreatePersonForm, LoginForm, UpdatePersonForm
from flask_login import current_user, login_required, login_user, logout_user

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    # user = {'username': 'Miguel'}
    # posts = [
    #     {
    #         'author': {'username': 'John'},
    #         'body': 'Beautiful day in Portland!'
    #     },
    #     {
    #         'author': {'username': 'Susan'},
    #         'body': 'The Avengers movie was so cool!'
    #     }
    # ]
    if current_user.is_admin:
        persons = models.get_all_persons()
        return render_template('personen.html', title='Home', persons=persons)

    return redirect(url_for('depot_uebersicht'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        models.create_person(
            username="admin",
            password="123",
            first_name="Josef",
            last_name="Landmann",
            is_admin=True
        )
        models.create_person(
            username="max",
            password="123",
            first_name="Max",
            last_name="Mustermann",
            birth_date="1980-01-01",
            phone_number="+49123456789",
            profession="Software Engineer",
            is_admin=False
        )
    except Exception as e:
        print(e)
        
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = models.Person.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Ungültiger Username oder Passwort', 'danger')
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
            flash(form.firstname.data + " " + form.lastname.data + " erfolgreich erstellt", 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash("Person erstellen nicht erfolgreich: " + e.__str__, 'danger')
            return redirect(url_for('person_erstellen'))
    return render_template('person_erstellen.html', title='Person erstellen', form=form)

@app.route('/person_aktualisieren/<int:id>', methods=['GET', 'POST'])
@login_required
def update_person_details(id):
    if current_user.is_admin:
        form = UpdatePersonForm()
        if request.method == 'GET':
            form.id.data = id
            person = models.get_person(id)
            if person:
                form.username.data = person.username
                form.firstname.data = person.first_name
                form.lastname.data = person.last_name
                form.birthdate.data = person.birth_date
                form.phone_number.data = person.phone_number
                form.profession.data = person.profession
                form.is_admin.data = person.is_admin
        if form.validate_on_submit():
            try:
                models.update_person(person_id=form.id.data,
                                    username=form.username.data,
                                    password=form.password.data,
                                    first_name=form.firstname.data,
                                    last_name=form.lastname.data,
                                    birth_date=form.birthdate.data,
                                    phone_number=form.phone_number.data,
                                    profession=form.profession.data,
                                    is_admin=form.is_admin.data)
                flash("Person erfolgreich aktualisiert", 'success')
                return redirect(url_for('index'))
            except Exception as e:
                flash("Fehler beim Aktualisieren der Person: " + e.__str__, 'danger')
        return render_template('person_aktualisieren.html', form=form)
    flash("Keine Berechtigung zur Aktualisierung der Person", 'danger')
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
        
        flash("Test-Personen erfolgreich erstellt", 'success')
    except:
        flash("Fehler beim Erstellen der Test-Personen", 'danger')
    
    return redirect(url_for('index'))

# Depots der eingeloggten Person
@app.route('/depots', methods=['GET'])
@login_required
def depot_uebersicht():
    try:
        person = models.get_person(current_user.person_id)
        deposits = person.deposits
        return render_template('depots.html', title='Depotübersicht', person=person, deposits=deposits)
    except Exception as e:
        print(e)

@app.route('/personen/<int:person_id>/depots', methods=['GET'])
@login_required
def depots(person_id):
    try:
        person = models.get_person(person_id)
        if current_user.is_admin:
            deposits = person.deposits
            return render_template('depots.html', title='Depotübersicht', person=person, deposits=deposits)

        return render_template('depots.html', title='Depotübersicht')
    except Exception as e:
        print(e)

# Depot einer Person (nur für Admin)
@app.route('/personen/<int:person_id>/depots/<int:depot_id>', methods=['GET'])
@login_required
def depositByPerson(person_id, depot_id):
    try:
        person = models.get_person(person_id)
        if current_user.is_admin:
            deposit = models.get_deposit(depot_id)
            securities_positions = models.get_securities_positions_by_deposit(deposit.deposit_id)
            return render_template('depot.html', title=deposit.deposit_name, person=person, deposit=deposit, securities_positions=securities_positions)
    except Exception as e:
        print(e)

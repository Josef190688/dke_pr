from datetime import datetime
from flask import flash, make_response, redirect, render_template, request, url_for
import requests
from app import app, models, db, converter
from app.forms import CreatePersonForm, LoginForm, UpdatePersonForm, WertpapiereKaufenForm
from flask_login import current_user, login_required, login_user, logout_user

@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
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

# Depotübersicht der eingeloggten Person
@app.route('/depots', methods=['GET'])
@login_required
def depot_uebersicht():
    return depots(current_user.person_id)

# Depotübersicht einer Person (wenn Admin), sonst Depotübersicht der eingeloggten Person
@app.route('/personen/<int:person_id>/depots', methods=['GET'])
@login_required
def depots(person_id):
    try:
        person = None
        if current_user.is_admin:
            person = models.get_person(person_id)
        else:
            if (person_id != current_user.person_id):
                return redirect(url_for('depot_uebersicht'))
            person = models.get_person(current_user.person_id)
        if (person):
            deposits = person.deposits
            gesamtwert = 0.0
            for depot in deposits:
                positions = models.get_securities_positions_by_deposit(depot.deposit_id)
                price = 0.0
                for position in positions:
                    price += position.get_price()
                depot.gesamtwert = price
                gesamtwert += depot.gesamtwert
            return render_template('depots.html', title='Depotübersicht', person=person, deposits=deposits, gesamtwert=gesamtwert)
        return render_template('depots.html', title='Depotübersicht')
    except Exception as e:
        print(e)

# Depot der eingeloggten Person
@app.route('/depots/<int:depot_id>', methods=['GET'])
@login_required
def depot(depot_id):
    return depositByPerson(current_user.person_id, depot_id)

# Depot einer Person (nur für Admin)
@app.route('/personen/<int:person_id>/depots/<int:depot_id>', methods=['GET'])
@login_required
def depositByPerson(person_id, depot_id):
    try:
        person = None
        if current_user.is_admin:
            person = models.get_person(person_id)
        else:
            if (person_id != current_user.person_id):
                return redirect(url_for('depot', depot_id=depot_id))
            person = models.get_person(current_user.person_id)
        deposit = models.get_deposit(depot_id)
        securities_positions = models.get_securities_positions_by_deposit(deposit.deposit_id)
        for position in securities_positions:
            # Name des Wertpapiers der Position zuweisen
            response = requests.get(f'http://localhost:50051/firmen/wertpapiere/{position.security_id}')
            if response.status_code == 200:
                security = response.json()
                security_name = security['name']
                if security_name:
                    position.security_name = security_name
                security_currency = security['currency'] # TODO: sollte market_currency sein
                security_price = security['price']
                if security_currency and security_price:
                    # Formatierten Preis pro Stück der Position zuweisen
                    converted_amount = converter.convert(security_price, security_currency, person.account.displayed_currency)
                    formatted_amount = converter.format(converted_amount, person.account.displayed_currency)
                    position.formatted_price_per_piece = formatted_amount
                    # Gesamtpreis der Position zuweisen
                    position.formatted_total_price = converter.format(converted_amount * position.amount, person.account.displayed_currency)
                # Name der Börse der Position zuweisen
                response = requests.get(f'http://localhost:50052/markets/{position.market_id}', headers={'Accept': 'application/json'})
                market = response.json()
                market_name = market['market_name']
                if market_name:
                    position.market_name = market_name
        return render_template('depot.html', title=deposit.deposit_name, person=person, deposit=deposit, securities_positions=securities_positions)
    except Exception as e:
        print(e)

# Wertpapiere kaufen (nur für Admin)
@app.route('/personen/<int:person_id>/depots/<int:depot_id>/wertpapiere_kaufen', methods=['GET', 'POST'])
@login_required
def wertpapiere_kaufen(person_id, depot_id):
    form = WertpapiereKaufenForm()
    try:
        person = models.get_person(person_id)
        deposit = models.get_deposit(depot_id)
        if form.validate_on_submit():
            data = {
                'security_id': form.selectedWertpapierId.data,
                'amount': form.amount.data
            }
            data2 = {
                'id': form.selectedWertpapierId.data,
                'amount': form.amount.data,
                'comp_id': form.comp_id.data,
                'depot_id': form.depot_id.data,
                # 'price': entry.get('price')
                'currency' : form.currency.data
            }
            print(data2)
            response = requests.put(f"http://127.0.0.1:50052/markets/{form.selectedBoersenId.data}/buy", json=data)
            if response.status_code == 200:
                models.create_securities_position(security_id=form.selectedWertpapierId.data,
                                                  company_id=form.comp_id.data,
                                                  amount=form.amount.data,
                                                  market_id=form.selectedBoersenId.data,
                                                  purchase_timestamp=datetime.now(),
                                                  deposit_id=depot_id)
                flash('Kauf war erfolgreich', 'success')
                return redirect(url_for('depositByPerson', person_id=person_id, depot_id=depot_id))
            else:
                flash(response.text, 'error')
                return render_template('wertpapiere_kaufen.html', form=form, person=person, deposit=deposit)
        else:
            if current_user.is_admin:
                securities_positions = models.get_securities_positions_by_deposit(deposit.deposit_id)
                return render_template('wertpapiere_kaufen.html', form=form, person=person, deposit=deposit)
    except requests.RequestException as e:
        flash('Es ist ein Fehler aufgetreten. Bitte versuchen Sie es später erneut.', 'danger')
        return render_template('wertpapiere_kaufen.html', form=form, person=person, deposit=deposit)
    except Exception as e:
        flash('Ein interner Serverfehler ist aufgetreten. Bitte kontaktieren Sie den Administrator.', 'danger')
        print(e)
        return render_template('wertpapiere_kaufen.html', form=form, person=person, deposit=deposit)
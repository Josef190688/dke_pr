import csv
import io
from flask_login import current_user, login_required
import requests
from app import app, models, converter
from flask import Response, flash, make_response, redirect, request, jsonify, url_for

# CRUD Personen
# ------------------------------------------------------------------------------------------

# DELETE Person
@app.route('/api/personen/<int:person_id>', methods=['DELETE'])
@login_required
def delete_person(person_id):
    if current_user.is_admin:
        try:
            models.delete_person(person_id)
            flash("Person erfolgreich gelöscht", 'success')
            return make_response('Person erfolgreich gelöscht', 204)
        except Exception as e:
            print(e)
            flash("Person löschen nicht erfolgreich: " + e.__str__, 'danger')
    return redirect(url_for('index'))

# CRUD Konto
# ------------------------------------------------------------------------------------------

# UPDATE Konto
@app.route('/api/personen/<int:person_id>/einzahlen', methods=['POST'])
@login_required
def einzahlen(person_id):
    if current_user.is_admin:
        try:
            data = request.get_json()
            einzahlen = data.get('einzahlen')
            person = models.get_person(person_id)
            if einzahlen and person:
                amount = float(einzahlen)
                account = person.account
                account.update(account_balance_in_euro = account.account_balance_in_euro + amount)
                response_text = 'EUR ' + str(amount) + ' erfolgreich eingezahlt'
                flash(response_text, 'success')
                return make_response(response_text, 200)
        except Exception as e:
            return make_response(e.__str__, 400)
    return redirect(url_for('index'))

# UPDATE Konto
@app.route('/api/personen/<int:person_id>/auszahlen', methods=['POST'])
@login_required
def auszahlen(person_id):
    if current_user.is_admin:
        try:
            data = request.get_json()
            auszahlen = data.get('auszahlen')
            if not auszahlen:
                raise Exception('\'auszahlen\' im Body erwartet, aber nicht gefunden')
            person = models.get_person(person_id)
            if not person:
                raise Exception('Person mit der ID ' + person_id + ' nicht gefunden')
            if person and auszahlen:
                amount = float(auszahlen)
                account = person.account
                if account.account_balance_in_euro - amount < 0:
                    response_text = 'EUR ' + str(amount) + ' zum Auszahlen zu hoch. Auf dem Konto befinden sich EUR ' + str(account.account_balance_in_euro)
                    flash(response_text, 'danger')
                    return jsonify({'error': response_text}), 400
                account.update(account_balance_in_euro = account.account_balance_in_euro - amount)
                response_text = 'EUR ' + str(amount) + ' erfolgreich ausgezahlt'
                flash(response_text, 'success')
                return make_response(response_text, 200)
        except Exception as e:
            flash(e.__str__, 'danger')
            print(e)
            return make_response(e.__str__, 400)
    return redirect(url_for('index'))

# CRUD Depots
# ------------------------------------------------------------------------------------------

# CREATE Depot
@app.route('/api/personen/<int:person_id>/depots', methods=['POST'])
@login_required
def create_depot(person_id):
    if current_user.is_admin:
        try:
            person = models.get_person(person_id)
            if not person:
                return jsonify({'error': 'Person not found'}), 404
            
            data = request.get_json()
            deposit_name = data.get('deposit_name')
            if not deposit_name:
                return jsonify({'error': 'Depot name is required'}), 400
            
            deposit = models.create_deposit(person_id, deposit_name)
            return jsonify({'message': 'Depot created successfully', 'deposit': deposit.to_dict()}), 201
        except Exception as e:
            return jsonify({'error': e}), 500
        
# UPDATE Depot
@app.route('/api/personen/<int:person_id>/depots', methods=['PUT'])
@login_required
def update_depot(person_id):
    if current_user.is_admin:
        try:
            person = models.get_person(person_id)
            if not person:
                return jsonify({'error': 'Person not found'}), 404
            
            data = request.get_json()
            deposit_name = data.get('deposit_name')
            if not deposit_name:
                return jsonify({'error': 'Depot name is required'}), 400
            
            deposit = models.update_deposit(person_id, deposit_name)
            return jsonify({'message': 'Depot updated successfully', 'deposit': deposit.to_dict()}), 201
        except Exception as e:
            return jsonify({'error': e}), 500

# DELETE Depot
@app.route('/api/personen/<int:person_id>/depots/<int:deposit_id>', methods=['DELETE'])
@login_required
def delete_depot(person_id, deposit_id):
    if current_user.is_admin:
        try:
            person = models.get_person(person_id)
            if not person:
                return jsonify({'error': 'Person not found'}), 404

            deposit = models.get_deposit(deposit_id)
            if not deposit or deposit.person.person_id != person_id:
                return jsonify({'error': 'Deposit not found or does not belong to the person'}), 404
            
            models.delete_deposit(deposit_id)
            return jsonify({'message': 'Depot deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': e}), 500

# CRUD Depotpositionen
# ------------------------------------------------------------------------------------------

# GET Depotposition
@app.route('/api/depotpositionen/<int:position_id>', methods=['GET'])
@login_required
def get_deposit_by__deposit_id(position_id):
    if current_user.is_admin:
        return jsonify(models.get_securities_position(position_id).to_dict()), 200
    else:
        return jsonify({'error': 'Kein Admin'}), 400

# POST Depotposition - Verkauf
@app.route('/api/personen/<int:person_id>/depots/<int:deposit_id>/depotposition/<int:position_id>/verkauf', methods=['POST'])
@login_required
def sell(person_id, deposit_id, position_id):
    if current_user.is_admin:
        try:
            person = models.get_person(person_id)
            if not person:
                flash('Person nicht gefunden')
                return jsonify({'error': 'Person nicht gefunden'}), 404

            deposit = models.get_deposit(deposit_id)
            if not deposit or deposit.person.person_id != person_id:
                flash('Depot nicht gefunden oder gehört nicht zur Person')
                return jsonify({'error': 'Depot nicht gefunden oder gehört nicht zur Person'}), 404
            
            position = models.get_securities_position(position_id)
            if not position or position.deposit.deposit_id != deposit_id:
                flash('Depotposition nicht gefunden oder gehört nicht zum angegebenen Depot')
                return jsonify({'error': 'Depotposition nicht gefunden oder gehört nicht zum angegebenen Depot'}), 404

            # Wertpapierpreis abfragen
            response = requests.get(f'http://localhost:50051/firmen/wertpapiere/{position.security_id}', headers={'Content-Type': 'application/json'})
            security_price = None
            if response.status_code == 200:
                security = response.json()
                security_price = security['price']
                security_currency = security['currency']
                response = requests.get(f'http://localhost:50052/markets/{position.market_id}', headers={'Accept': 'application/json'})
                if response.status_code == 200:
                    market = response.json()
                    market_currency = market['market_currency_code']

                    converted_price = "%.2f" % converter.convert(security_price, security_currency, market_currency)
                    fee_to_pay = float("%.2f" % converter.convert(market['market_fee'], market_currency, 'EUR'))
                    
                    print(converted_price)
                    data = {
                        'id': position.security_id,
                        'amount': position.amount,
                        'depot_id': deposit.deposit_id,
                        'price': converted_price,
                        'currency': market_currency
                    }
                    response = requests.post(f'http://localhost:50052/markets/{position.market_id}/offer', json=data, headers={'Content-Type': 'application/json'})
                    if response.status_code == 200:
                        person.account.update(account_balance_in_euro = person.account.account_balance_in_euro - fee_to_pay)
                        models.delete_securities_position(position.securities_position_id)
                        flash('Wertpapier erfolgreich zum Verkauf angeboten')
                        return jsonify({'message': 'Wertpapier erfolgreich zum Verkauf angeboten'}), 200
                    else:
                        return jsonify({'error': response.text}), response.status_code
                else:
                    flash(response.text)
                    return jsonify({'error': response.text}), response.status_code
            else:
                flash(response.text)
                return jsonify({'error': response.text}), response.status_code
        except Exception as e:
            flash(e)
            return jsonify({'error': e}), 500
        
# CSV
# ------------------------------------------------------------------------------------------
@app.route('/api/personen/<int:person_id>/depots/csv')
@login_required
def export_csv(person_id):
    person = models.get_person(person_id)
    portfolio_data = []
    deposits = person.deposits
    for deposit in deposits:
        for position in deposit.securities_positions:
            wertpapier_name = position.security_id
            preis = 'unbekannt'
            try:
                response = requests.get(f'http://localhost:50051/firmen/wertpapiere/{position.security_id}', headers={'Content-Type': 'application/json'})
                if response.status_code == 200:
                    security = response.json()
                    wertpapier_name = security['name']
                    preis = converter.convert(security['price'], security['currency'], 'EUR')
                    preis = round(preis, 2)
            except Exception as e:
                print(e)    
            portfolio_data.append(
                {
                    'Depotname': deposit.deposit_name,
                    'Wertpapier': wertpapier_name,
                    'Anzahl': position.amount,
                    'Preis pro Stück in EUR': preis
                }
            )

    filename = f"portfolio_{person.last_name}_{person.first_name}.csv"

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=portfolio_data[0].keys())
    writer.writeheader()
    writer.writerows(portfolio_data)
    output = output.getvalue()

    response = Response(output, mimetype='text/csv')
    response.headers['Content-Disposition'] = f'attachment; filename={filename}'
    return response
        
# Öffentliche API
# ------------------------------------------------------------------------------------------

# Nachricht erhalten, wenn ein Wertpapier eines Depots verkauft wurde
@app.route('/depot/wertpapier/verkauf/<int:depot_id>', methods=['PUT'])
def wertpapier_verkauft(depot_id):
    data = request.get_json()
    print('Verkauf Wertpapier, Depot ID: ' + str(depot_id))
    print('Received data:', data)
    price = data.get('price')
    currency = data.get('currency')
    converted_price = "%.2f" % converter.convert(price, currency, 'EUR')
    depot = models.get_deposit(depot_id)
    if depot:
        account = depot.person.account
        print(depot.person.first_name + ' ' + depot.person.last_name + ' hat Wertpapiere verkauft und bekommt:', price, currency)
        account.update(account_balance_in_euro = account.account_balance_in_euro + float(converted_price))
        flash('Wertpapiere von Depot ' + str(depot_id) + 'wurden verkauft.', 'success')
    return f"Verkauf von Wertpapier mit der ID {depot_id}"

# CurrencyConverter
@app.route('/currency_converter/<float:amount>/<string:from_currency>/<string:to_currency>', methods=['GET'])
def convert(amount, from_currency, to_currency):
    return str(converter.convert(amount, from_currency, to_currency))

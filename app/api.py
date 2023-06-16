from flask_login import current_user, login_required
from app import app, models
from flask import flash, make_response, redirect, request, jsonify, url_for

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
@app.route('/api/personen/<int:person_id>/depots', methods=['PUT'])
@login_required
def create_depot(person_id):
    if current_user.is_admin:
        try:
            person = models.get_person(person_id)
            if not person:
                return jsonify({'error': 'Person not found'}), 404

            data = request.get_json()
            deposit_name = data.get('deposit_name')
            # TODO auch andere werte (kontostand, displayed currency)

            # Validiere und erstelle das Depot
            if not deposit_name:
                return jsonify({'error': 'Depot name is required'}), 400

            # Depot erstellen und der Person zuordnen
            deposit = models.create_deposit(person_id, deposit_name)

            # Gib die Erfolgsnachricht oder das erstellte Depot zurück
            return jsonify({'message': 'Depot created successfully', 'deposit': deposit.to_dict()}), 201
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

# DELETE Depotposition
@app.route('/api/personen/<int:person_id>/depots/<int:deposit_id>/depotposition/<int:position_id>', methods=['DELETE'])
@login_required
def sell(person_id, deposit_id, position_id):
    if current_user.is_admin:
        try:
            person = models.get_person(person_id)
            if not person:
                return jsonify({'error': 'Person nicht gefunden'}), 404

            deposit = models.get_deposit(deposit_id)
            if not deposit or deposit.person.person_id != person_id:
                return jsonify({'error': 'Depot nicht gefunden oder gehört nicht zur Person'}), 404
            
            position = models.get_securities_position(position_id)
            if not position or position.deposit.deposit_id != deposit_id:
                return jsonify({'error': 'Depotposition nicht gefunden oder gehört nicht zum angegebenen Depot'}), 404

            models.delete_securities_position(position.securities_position_id)
            return jsonify({'message': 'Depotposition erfolgreich gelöscht'}), 200
        except Exception as e:
            return jsonify({'error': e}), 500
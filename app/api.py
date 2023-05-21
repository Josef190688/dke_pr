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
            # flash("Person erfolgreich gelöscht")
            return make_response('Person erfolgreich gelöscht', 204)
        except Exception as e:
            print(e)
            # flash("Person löschen nicht erfolgreich")
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

            # Hole die erforderlichen Daten aus dem Request Body
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
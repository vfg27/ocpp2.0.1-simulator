import json
from typing import Any

from flask import Flask, jsonify, request
from db import add_event, auth_user, add_user, check_user, chg_password, get_events


app = Flask(__name__)


def _get_message(message: Any, code: int = 200):
    return jsonify({'message': message, 'code': code}), code


@app.route('/api/reserve_now/<serial_number>', methods=['GET', 'PUT', 'POST'])
def reserve_now(serial_number: str):
    # Get request parameters
    token = {
        'type': request.args.get('type', None, type=str),
        'id_token': request.args.get('id_token', None, type=str),
    }

    # Check token is set correctly
    if token['type'] is None or token['id_token'] is None:
        return _get_message('Bad request', 400)
    
    # Add event to DB
    add_event('reserve_now', serial_number, token)

    return _get_message('OK')

@app.route('/api/list/<serial_number>', methods=['GET', 'PUT', 'POST'])
def list(serial_number: str):
    # Get request parameters
    token = {
        'type': request.args.get('type', None, type=str),
        'id_token': request.args.get('id_token', None, type=str),
    }

    # Check token is set correctly
    if token['type'] is None or token['id_token'] is None:
        return _get_message('Bad request', 400)
    
    # Add event to DB
    list = get_events(serial_number, token)
    print('*********************************************************************************************')
    print(list)

    return _get_message(list)

@app.route('/api/login', methods=['GET', 'PUT', 'POST'])
def login():
    # Get request parameters
    token = {
        'serial': request.args.get('serial', None, type=str),
        'password': request.args.get('password', None, type=str),
    }
    
    # Check token is set correctly
    if token['serial'] is None or token['password'] == '':
        return _get_message('Bad request', 400)
    
    if check_user(token['serial']) != None:
        return _get_message('User already exists', 403)

    # Add user to DB
    add_user(token['serial'], token['password'])

    return _get_message('OK')

@app.route('/api/change_password', methods=['GET', 'PUT', 'POST'])
def change_password():
    # Get request parameters
    token = {
        'serial': request.args.get('serial', None, type=str),
        'old_password': request.args.get('old_password', None, type=str),
        'new_password': request.args.get('new_password', None, type=str),
    }
    
    # Check token is set correctly
    if token['serial'] is None or token['old_password'] == '' or token['new_password'] == '':
        return _get_message('Bad request', 400)
    
    if not auth_user(token['serial'], token['old_password']):
        return _get_message('Wrong password', 404)

    # Add user to DB
    chg_password(token['serial'], token['new_password'])

    return _get_message('OK')


'''
@app.get('/api/get/<serial_number>')
def test_get(serial_number: str):
    return _get_message(get_event('reserve_now', serial_number))
'''


if __name__ == '__main__':
    app.run(host='fe80::e3a6:46e4:bff9:fb8e%ens33', port=8000)

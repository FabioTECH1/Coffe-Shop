# from crypt import methods
import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUNpip
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES

# GET drinks


@app.route('/drinks', methods=['GET'])
def drinks():
    try:
        drinks = Drink.query.all()
        drinks = [drink.short() for drink in drinks]

        return jsonify({
            'status code': 200,
            'success': True,
            'drinks': drinks
        })
    except:
        abort(404)


# GET drinks detail
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def drink_details(payload):
    try:
        drinks = Drink.query.all()
        drinks = [drink.long() for drink in drinks]

        return jsonify({
            'status code': 200,
            'success': True,
            'drinks': drinks
        })
    except:
        abort(404)


#  Add new drink
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    try:
        body = request.get_json()
        title = body.get('title')
        recipe = json.dumps(body.get('recipe'))
        new_drink = Drink(title=title, recipe=recipe)
        new_drink.insert()

        return jsonify({
            'status code': 200,
            'success': True,
            'drinks': [new_drink.long()]
        })
    except:
        abort(422)


# Edit and update existing drink/<id>
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):
    try:
        body = request.get_json()
        title = body.get('title')
        recipe = json.dumps(body.get('recipe', None))

        drink = Drink.query.filter(Drink.id == id).one_or_none()

        if drink is None:
            abort(404)

        if recipe is not None:
            drink.recipe = recipe

        drink.title = title
        drink.update()
        drink = Drink.query.get(id)

        return jsonify({
            'status code': 200,
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        abort(404)


# DELETE a drink
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    try:
        drink = Drink.query.filter_by(
            id=id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()

        return jsonify({
            'status code': 200,
            'success': True,
            'delete': id
        })
    except:
        abort(422)


# Error 422 Handling
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

# Error 404 Handling


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


# auth error Handling
@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response

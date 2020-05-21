from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# ROUTES

@app.route('/drinks')
def get_drinks():
    drinks = [drink.short() for drink in Drink.query.all()]

    return jsonify({"success": True, "drinks": drinks})


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    drinks = [drink.long() for drink in Drink.query.all()]

    return jsonify({"success": True, "drinks": drinks})


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(payload):
    try:
        data = request.get_json()

        title = data['title']
        recipe = data['recipe']

        new_drink = Drink(title=title, recipe=json.dumps(recipe))
        new_drink.insert()
    except Exception:
        abort(400)

    return jsonify({'success': True, 'drinks': [new_drink.long()]})


@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drinks(payload, id):
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)

    try:
        data = request.get_json()

        if 'title' in data:
            drink.title = data['title']

        if 'recipe' in data:
            drink.recipe = json.dumps(data['recipe'])

        drink.update()
    except Exception:
        abort(400)

    return jsonify({'success': True, 'drinks': [drink.long()]})


@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)

    try:
        drink.delete()

    except Exception:
        abort(400)

    return jsonify({'success': True, 'delete': id})


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(400)
def bad_request(error):
    return jsonify({'success': False,
                    'error': 400,
                    'message': 'bad request'
                    }), 400


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({'success': False,
                    'error': 405,
                    'message': 'method not allowed'
                    }), 405


@app.errorhandler(500)
def server_error(error):
    return jsonify({'success': False,
                    'error': 500,
                    'message': 'Internal server error'
                    }), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def authorization_error(AuthError):
    return jsonify({
        "success": False,
        "error": AuthError.status_code,
        "message": AuthError.error['description']
    }), 401

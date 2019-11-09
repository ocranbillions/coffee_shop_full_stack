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
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

# # SEED SAMPLE DRINK
# drink = Drink(
#     title='chocolate milk',
#     recipe='[{"name": "chocolate", "color": "brown", "parts": 1},{"name": "milk", "color": "cream", "parts": 3}]'
# )
# Drink.insert(drink)

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    try:
        drinks_results = Drink.query.all()
        drinks = [drink.short() for drink in drinks_results]

        return jsonify({
            'success': True,
            'drinks': drinks,
        }), 200
        
    except:
        abort(500)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        drinks_results = Drink.query.all()
        drinks = [drink.long() for drink in drinks_results]

        return jsonify({
            'success': True,
            'drinks': drinks,
        }), 200
        
    except:
        abort(500)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(jwt):
    try:
        data = request.get_json()
        title = data.get('title')
        recipe_raw = data.get('recipe')
        recipe = json.dumps(recipe_raw)

        drink = Drink(title=title, recipe=recipe)
        drink.insert()
        return jsonify({
            'success': True,
            'drinks': drink.long(),
        }), 200
    except:
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):
    notFound = False
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            notFound = True
    
        else:
            title = request.json.get('title')

            if type(title) is not str or len(title) is 0:
                abort(400)

            drink.title = title
            drink.update()
            
            return jsonify({
                'success': True,
                'drink': [drink.long()],
            })
    except:
        abort(422)
    finally:
        if notFound is True:
            abort(404)



'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
    notFound = False
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        if drink is None:
            notFound = True
        else:
            drink.delete()
            return jsonify({
                'success': True,
                'delete': drink_id,
            })
    except:
        abort(500)
    finally:
        if notFound is True:
            abort(404)



## Error Handling
# handle not found resources
@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

# handle unprocessable entities
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
    }), 422


# handle internal server errors
@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
# handle user inputs
@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request, please check your inputs"
    }), 400

# handle unauthorized request errors
@app.errorhandler(401)
def unathorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": error.description,
    }), 401

# handle forbidden requests
@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "You are forbidden from accessing this resource",
    }), 403

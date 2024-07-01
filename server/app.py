#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response,jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def restaurants():
    if request.method == 'GET':
        restaurants=[]
        for restaurant in Restaurant.query.all():
            restaurant_dict={
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
            restaurants.append(restaurant_dict)
        response = make_response(
            jsonify(restaurants),200
        )
        return response
       
    
@app.route('/restaurants/<int:id>', methods=['GET','DELETE'])
def get_restaurant_by_id(id):
    restaurant = db.session.get(Restaurant, id)
    if request.method == 'GET':
        if restaurant:
            restaurant_dict = {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address,
                "restaurant_pizzas": [{
                    "pizza_id": restaurant_pizzas.pizza_id,
                    "restaurant_id": restaurant_pizzas.restaurant_id,
                    "price": restaurant_pizzas.price,
                    "pizza": {
                        "name": restaurant_pizzas.pizza.name,
                        "ingredients": restaurant_pizzas.pizza.ingredients
                    }
                } for restaurant_pizzas in restaurant.restaurant_pizzas]
            }
            response = make_response(
                jsonify(restaurant_dict), 200
            )
            return response
        else:
            response = make_response(
                jsonify({"error": "Restaurant not found"}), 404
            )
            return response

    elif request.method == 'DELETE':
        if restaurant:
            db.session.delete(restaurant)
            db.session.commit()
            response = make_response('', 204)
            return response
        else:
            response = make_response(
                jsonify({"error": "Restaurant not found"}), 404
            )
            return response
        
@app.route('/pizzas', methods=['GET'])
def pizzas():
    if request.method == "GET":
        pizzas=[]
        for pizza in Pizza.query.all():
            pizza_dict={
                "id":pizza.id,
                "name":pizza.name,
                "ingredients":pizza.ingredients
            }
            pizzas.append(pizza_dict)
    response=make_response(
        jsonify(pizzas),200
    )
    return response

@app.route('/restaurant_pizzas', methods=['GET', 'POST'])
def create_restaurant_pizzas():
    if request.method == 'GET':
        try:
            restaurant_pizzas = []
            for restaurant_pizza in RestaurantPizza.query.all():
                restaurant_pizza_dict = {
                    "id": restaurant_pizza.id,
                    "price": restaurant_pizza.price,
                    "pizza_id": restaurant_pizza.pizza_id,
                    "restaurant_id": restaurant_pizza.restaurant_id,
                    "pizza": restaurant_pizza.pizza.to_dict(only=("id", "name", "ingredients")),
                    "restaurant": restaurant_pizza.restaurant.to_dict(only=("id", "name", "address"))
                }
                restaurant_pizzas.append(restaurant_pizza_dict)

            response = jsonify(restaurant_pizzas)
            response.status_code = 200
            return response

        except Exception as error:
            response = jsonify({"errors": [str(error)]})
            response.status_code = 500
            return response

    elif request.method == 'POST':
        try:
            data = request.get_json()

            price = data.get("price")
            pizza_id = data.get("pizza_id")
            restaurant_id = data.get("restaurant_id")

            if price is None or not (1 <= price <= 30):
                response = jsonify({"errors": ["validation errors"]})
                response.status_code = 400
                return response

            pizza = db.session.get(Pizza, pizza_id)
            restaurant = db.session.get(Restaurant, restaurant_id)

            if not pizza:
                response = jsonify({"errors": ["Invalid pizza_id"]})
                response.status_code = 400
                return response
            if not restaurant:
                response = jsonify({"errors": ["Invalid restaurant_id"]})
                response.status_code = 400
                return response

            new_restaurant_pizza = RestaurantPizza(
                price=price,
                pizza_id=pizza_id,
                restaurant_id=restaurant_id
            )
            db.session.add(new_restaurant_pizza)
            db.session.commit()

            restaurant_pizza_dict = {
                "id": new_restaurant_pizza.id,
                "price": new_restaurant_pizza.price,
                "pizza_id": new_restaurant_pizza.pizza_id,
                "restaurant_id": new_restaurant_pizza.restaurant_id,
                "pizza": new_restaurant_pizza.pizza.to_dict(only=("id", "name", "ingredients")),
                "restaurant": new_restaurant_pizza.restaurant.to_dict(only=("id", "name", "address"))
            }

            response = jsonify(restaurant_pizza_dict)
            response.status_code = 201
            return response

        except Exception as error:
            response = jsonify({"errors": [str(error)]})
            response.status_code = 500
            return response


if __name__ == "__main__":
    app.run(port=5555, debug=True)
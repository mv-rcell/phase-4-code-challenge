#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

class HeroList(Resource):
    def get(self):
        heroes = Hero.query.all()
        return jsonify([hero.to_dict() for hero in heroes])

class HeroDetail(Resource):
    def get(self, hero_id):
        hero = Hero.query.get(hero_id)
        if hero:
            return jsonify({
                **hero.to_dict(),
                "hero_powers": [hp.to_dict() for hp in hero.hero_powers]
            })
        return make_response(jsonify({"error": "Hero not found"}), 404)

class PowerList(Resource):
    def get(self):
        powers = Power.query.all()
        return jsonify([power.to_dict() for power in powers])

class PowerDetail(Resource):
    def get(self, power_id):
        power = Power.query.get(power_id)
        if power:
            return jsonify(power.to_dict())
        return make_response(jsonify({"error": "Power not found"}), 404)

class HeroPowerList(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_hero_power = HeroPower(
                strength=data['strength'],
                hero_id=data['hero_id'],
                power_id=data['power_id']
            )
            db.session.add(new_hero_power)
            db.session.commit()
            return jsonify(new_hero_power.to_dict()), 201
        except ValueError as e:
            return make_response(jsonify({"errors": [str(e)]}), 400)

# Register the resources with Flask-RESTful
api.add_resource(HeroList, '/heroes')
api.add_resource(HeroDetail, '/heroes/<int:hero_id>')
api.add_resource(PowerList, '/powers')
api.add_resource(PowerDetail, '/powers/<int:power_id>')
api.add_resource(HeroPowerList, '/hero_powers')


@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


if __name__ == '__main__':
    app.run(port=5555, debug=True)

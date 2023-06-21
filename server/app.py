#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
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

api=Api(app)

@app.route('/')
def home():
    return ''

class Campers(Resource):
    def get(self):
        try:
            campers = Camper.query.all()
            all_campers = []
            for camper in campers:
                all_campers.append(camper.to_dict(only=("id", "name", "age")))
            return all_campers, 200
        except:
            return {"error": "400: Bad Request"}, 400
        
    def post(self):
        try:
            new_camper = Camper(
                name=request.json['name'],
                age=request.json['age']
            )
            db.session.add(new_camper)
            db.session.commit()
            return new_camper.to_dict(only=("id", "name", "age")), 201
        except:
            return {"errors": "400: validation error"}, 400
    
api.add_resource(Campers, "/campers")

class CampersById(Resource):
    def get(self, id):
        try:
            campers = Camper.query.filter_by(id=id).first().to_dict()
            return make_response(jsonify(campers), 200)
        except:
            return {"error": "Camper not found"}, 404
        
    def patch(self, id):
        try:
            camper = Camper.query.filter_by(id=id).first()
            if not camper:
                return {"error": "Camper not found"}, 404

            if 'name' in request.json:
                name = request.json['name']
                if name != '' and not isinstance(name, str):
                    raise ValueError("Invalid name")
                setattr(camper, 'name', name)

            if 'age' in request.json:
                age = request.json['age']
                if age is not None and not isinstance(age, int):
                    raise ValueError("Invalid age")
                setattr(camper, 'age', age)

            db.session.add(camper)
            db.session.commit()
            return camper.to_dict(), 202

        except:
            return {"errors": ["validation errors"]}, 400
        
api.add_resource(CampersById, "/campers/<int:id>")

class Activities(Resource):
    def get(self):
        try:
            activities = [activity.to_dict() for activity in Activity.query.all()]
            return activities, 200
        except:
            return {"error": "400: Bad Request"}, 400

api.add_resource(Activities, "/activities")

class ActivityById(Resource):
    def patch(self, id):
        try:
            activity = Activity.query.filter_by(id=id).first()
            if request.json['name']:
                setattr(activity, 'name', request.json['name'])
            db.session.add(activity)
            db.session.commit()
            return activity.to_dict(), 202
        except:
            raise Exception('error')
    
    def delete(self, id):
        try:
            activity = Activity.query.filter_by(id=id).first()
            db.session.delete(activity)
            db.session.commit()
            return make_response("", 204)
        except:
            return {"error": "Activity not found"}, 404
    
        
api.add_resource(ActivityById, "/activities/<int:id>")


class Signups(Resource):
    def post(self):
        data = request.get_json()
        try:
            signup = Signup(
                time=data.get('time'),
                camper_id=data.get('camper_id'),
                activity_id=data.get('activity_id'))
            db.session.add(signup)
            db.session.commit()
        except:
            return {"errors": ["validation errors"]}, 400
        return signup.to_dict(), 201
        
api.add_resource(Signups, "/signups")

if __name__ == '__main__':
    app.run(port=5555, debug=True)

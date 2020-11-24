import os
import json
import datetime
from flask import Flask
from flaskr.models.measure import Measure
from bson.objectid import ObjectId
from .database import mongo

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        MONGO_URI='mongodb+srv://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' 
                   + os.environ['MONGODB_HOST'] + '/' + os.environ['MONGODB_DATABASE'] + '?retryWrites=true&w=majority',
        SECRET_KEY="DEV"
        #SECRET_KEY=os.environ['SECRET_KEY']
    )

    # Connect with mongo and store the connection pool
    mongo.init_app(app)

    #Using JsonEnconder for mongo ObjectId and date
    class JsonEnconder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, ObjectId):
                return str(o)
            if isinstance(o, datetime.datetime):
                return str(o)
            return json.JSONEncoder.default(self, o)

    app.json_encoder = JsonEnconder

    # Registering blueprints
    from . import auth, measure
    app.register_blueprint(auth.bp)
    app.register_blueprint(measure.bp)
    
    app.add_url_rule('/', endpoint='index')
    return app

app = create_app()
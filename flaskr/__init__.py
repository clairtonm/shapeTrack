import os
from flask import Flask, render_template, request, redirect, flash
from flaskr.measure import Measure
from flask_pymongo import PyMongo


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY= 'dev',
        MONGO_URI='mongodb+srv://' + os.environ['MONGODB_USERNAME'] + ':' + os.environ['MONGODB_PASSWORD'] + '@' 
                   + os.environ['MONGODB_HOST'] + '/' + os.environ['MONGODB_DATABASE'] + '?retryWrites=true&w=majority'
    )

    mongo = PyMongo(app)
    db = mongo.db

    user = {"name":"user_test"}

    result = db.users.insert_one(user)

    print(result.acknowledged)

    app_users = db.users.find()
    for app_user in app_users:
        print(app_user['name'])

    measures = []

    @app.route('/', methods=['POST', 'GET'])
    def index():
        if request.method == 'POST':
            weight = request.form['weight-input']
            height = request.form['height-input']
            date = request.form['date-input']

            if (not weight) or (not height) and (not date):
                error = "You need to fill date and one more field!"
                return render_template('index.html', measures=measures, error=error)

            new_measure = Measure(weight, height, date)
            measures.append(new_measure)
            flash("Measure added")
            return redirect('/')
        else:
            return  render_template('index.html', measures=measures)

    return app
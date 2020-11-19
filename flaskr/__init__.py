from flask import Flask, render_template, request, redirect, flash
from flaskr.measure import Measure


def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY= 'dev'
    )

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
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from .database import mongo
from .models.measure import Measure
import datetime
from flaskr.auth import login_required
from bson.objectid import ObjectId
from bson.codec_options import CodecOptions
import pytz
from tzlocal import get_localzone

bp = Blueprint("measure", __name__)
db = mongo.db

@bp.route("/", methods=['POST', 'GET'])
@login_required
def index():    
    measures = []

    # Converte the timezone when get the datetime from mongodb
    aware_timez = db.measures.with_options(codec_options=CodecOptions(
    tz_aware=True,
    tzinfo=pytz.timezone(get_localzone().zone)))

    if request.method == 'POST':
            weight = request.form['weight-input']
            height = request.form['height-input']

            if (not weight) or (not height): 
                flash('You need to fill weight field!', 'error')
                return render_template('index.html', measures=measures)

            db.measures.insert_one({
                "user_id" : g.user['_id'],
                "weight" : weight,
                "height" : height,
                "created_at" : datetime.datetime.utcnow()
            })
            flash('Measure added', 'success')

            for measure in aware_timez.find({"user_id": g.user['_id']}):
                measures.append(Measure(measure['weight'], 
                                        measure['height'], 
                                        measure['created_at'].date()))
            return render_template('index.html', measures=measures)
    else:        
        for measure in aware_timez.find({"user_id": g.user['_id']}):
                measures.append(Measure(measure['weight'], 
                                        measure['height'], 
                                        measure['created_at'].date()))
        return  render_template('index.html', measures=measures)

@bp.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = (db.users.find_one({"_id": ObjectId(user_id)}))
        
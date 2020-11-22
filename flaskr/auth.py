import functools
import datetime

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from .database import mongo
from bson.objectid import ObjectId

bp = Blueprint('auth', __name__, url_prefix='/auth')

db = mongo.db

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['inputName']
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        error = None

        if not username:
            error = 'Username is required'
        elif not email:
            error = 'Email is required'
        elif not password:
            error = 'Password is required'
        elif (db.users.find_one({"name": username}) is not None):
            error = 'User {} is already registered'.format(username)
        elif (db.users.find_one({"email": email}) is not None):
            error = 'Email {} is already registered'.format(email)
        
        if error is None:
            db.users.insert_one(
                {
                    "name": username, 
                    "email": email, 
                    "password": generate_password_hash(password),
                    "created_at": datetime.datetime.utcnow()
                })
            return redirect(url_for('auth.login'))

        app_users = db.users.find()
        for app_user in app_users:
            print(app_user['name'])
        
        flash(error, 'error')
    
    return render_template('auth/register.html')

@bp.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['inputEmail']
        password = request.form['inputPassword']
        error = None

        user = db.users.find_one({"email": email})

        if user is None:
            error = "Incorrect Email, {} not found!".format(email)
        elif not check_password_hash(user['password'], password):
            error = "Incorrect password."
        
        if error is None:
            session.clear()
            session['user_id'] = user['_id']
            return redirect(url_for('index'))

        flash(error, 'error')
    return render_template('auth/login.html')

@bp.before_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = (db.users.find_one({"_id": ObjectId(user_id)}))

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not hasattr(g, "user") or g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    return wrapped_view
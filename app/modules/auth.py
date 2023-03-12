import os
import jwt
import flask
import bcrypt
import datetime
import binascii

from modules import db
from modules import log

jwt_secret = ""
admin_password = ""

users = {}

# Helper functions
def init():
    global jwt_secret, admin_password
    admin_password = binascii.b2a_hex(os.urandom(16)).decode('utf-8')
    try:
        if db.data["settings"]["password"] != "":
            admin_password = db.data["settings"]["password"]
    except:
        pass

    db.data["settings"]["password"] = admin_password

    # Create admin user
    users["admin"] = {
        "username": "admin",
        "hash": bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()),
        "last_login": "Never",
    }

    print("Admin password: " + admin_password)



    # Randomly generate jwt secret
    jwt_secret = binascii.b2a_hex(os.urandom(16))

def current_user():
    global jwt_secret, users
    try:
        username = jwt.decode(flask.request.cookies.get('auth'), jwt_secret, algorithms=["HS256"])['username']
        if username in users:
            return users[username]
    except:
        pass
    return None


# Frontend functions
def login():
    return flask.render_template('login.html')

def logout():
    return logout_post_basic()

def view_users():
    global users
    return flask.render_template('users.html', users = users)

# Backend functions
def auth():
    # Check if path starts with /static
    if flask.request.path.startswith('/static'):
        return None
    # Check if path is /login
    if flask.request.path == '/login':
        return flask.render_template('login.html')
    if flask.request.path == '/api/login':
        return login_post_basic()
    if current_user() is None:
        return flask.redirect('/login', messages = ["You must be logged in to view this page"])
    return None

def login_post_basic():
    global admin_password, jwt_secret, users
    # Get username and password
    username = flask.request.form['username']
    password = flask.request.form['password']
    # Validate username and password
    if username in users and users[username]["hash"] == bcrypt.hashpw(password.encode('utf-8'), users[username]["hash"]):
        # Create JWT token
        token = jwt.encode({'username': username}, jwt_secret, algorithm="HS256")
        # Set auth cookie
        response = flask.make_response(flask.redirect('/'))
        response.set_cookie('auth', token, max_age=60*60*12)
        # Update last login
        users[username]["last_login"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.log("Login succeeded " + username + " from " + flask.request.remote_addr, "auth")
        return response
    else:
        log.log("Invalid login attempt: " + username + ":" + password + " from " + flask.request.remote_addr, "auth")
        return flask.redirect('/login')
    
def logout_post_basic():
    response = flask.make_response(flask.redirect('/login'))
    response.set_cookie('auth', '', expires=0)
    return response

def create_user():
    global users
    username = flask.request.form.get("thing1")
    password = flask.request.form.get("thing2")
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    if username in users:
        return flask.redirect("/users?messages=Username+already+exists")
    users[username] = {"username": username, "hash": hashed, "last_login": "Never"}
    return flask.redirect("/users?messages=User+created")
    

def delete_user():
    global users
    username = flask.request.args.get("username")
    if username not in users:
        return flask.redirect("/users?messages=Username+does+not+exist")
    del users[username]
    return flask.redirect("/users?messages=User+deleted")

def change_password():
    global jwt_secret, users
    password = flask.request.form.get("thing2")
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    username = current_user()["username"]
    users[username]["hash"] = hashed
    response = flask.make_response(flask.redirect('/login?messsages=Password+changed'))
    response.set_cookie('auth', '', expires=0)
    return response
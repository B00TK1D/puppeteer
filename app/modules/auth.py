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

def validate(token):
    global jwt_secret
    try:
        decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        if decoded['username'] == 'admin':
            return True
        elif decoded['username'] in users:
            return True
    except:
        return False
    return False


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
    # Get auth cookie
    token = flask.request.cookies.get('auth')
    if token is None:
        return flask.redirect('/login')
    if not validate(token):
        return flask.redirect('/login')
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
    username = flask.request.form.get("username")
    password = flask.request.form.get("password")
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    if username in users:
        return flask.redirect("/users?message=User+" + str(username) + "+already+exists")
    users[username] = {"username": username, "hash": hashed, "last_login": "Never"}
    return flask.redirect("/users?message=User+" + str(username) + "+created")
    

def delete_user():
    global users
    username = flask.request.form.get("username")
    if username not in users:
        return flask.redirect("/users?message=User+" + str(username) + "+does+not+exist")
    del users[username]
    return flask.redirect("/users?message=User+" + str(username) + "+deleted")
import os
import jwt
import flask
import binascii

import db
import log

jwt_secret = ""
admin_password = ""

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

    print("Admin password: " + admin_password)

    # Randomly generate jwt secret
    jwt_secret = binascii.b2a_hex(os.urandom(16))

def validate(token):
    global jwt_secret
    try:
        decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        if decoded['username'] == 'admin':
            return True
    except:
        return False
    return False


# Frontend functions
def login():
    return flask.render_template('login.html')

def logout():
    return logout_post_basic()


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
    global admin_password, jwt_secret
    # Get username and password
    username = flask.request.form['username']
    password = flask.request.form['password']
    # Validate username and password
    if username == "admin" and password == admin_password:
        # Create JWT token
        token = jwt.encode({'username': username}, jwt_secret, algorithm="HS256")
        # Set auth cookie
        response = flask.make_response(flask.redirect('/'))
        response.set_cookie('auth', token)
        log.log("Login succeeded " + username + " from " + flask.request.remote_addr, "auth")
        return response
    else:
        log.log("Invalid login attempt: " + username + ":" + password + " from " + flask.request.remote_addr, "auth")
        return flask.redirect('/login')
    

def logout_post_basic():
    response = flask.make_response(flask.redirect('/login'))
    response.set_cookie('auth', '', expires=0)
    return response
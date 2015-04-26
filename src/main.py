# -*- coding: utf-8 -*-

from flask import Flask,render_template, g, session, redirect, url_for, escape, request
import os
import user
import database

from config import DATABASE

app = Flask(__name__)
app.secret_key = os.urandom(24)



@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/sqltest")
def sqltest():
    q = database.query("SELECT * FROM bike")
    res = ""
    for i in q:
        for j in i:
            res += str(j)
        res += "\n"
    return "RAW BIKE LIST : " + res


@app.route("/")
def index():
    return render_template("home.html")

@app.route('/session_status')
def session_status():
    if user.isConnected():
        return 'Logged in as %s' % escape(user.getUserName())
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if user.checkLoginPassword(request.form['inputUsername'],request.form['inputPassword']):
            user.connectUser(request.form['inputUsername'])
            return redirect(url_for('index'))
        else:
            return render_template("login.html",loginFailure=True)
    else:
        return render_template("login.html")

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        pass # TODO
    # userPassword
    # userBankData
    # userLastName
    # userFirstName
    # userStreet
    # userNumber
    # userBox
    # userPostalCode
    # userCity
    # userCountry
    # userPhone
    else:
        return render_template("inscription.html")

@app.route("/station")
def station():
    return render_template("station.html")

@app.route("/trip")
def trip():
    if not user.isConnected():
        return redirect(url_for('login'))
    return render_template("trip.html")


@app.route("/history")
def history():
    if not user.isConnected():
        return redirect(url_for('login'))
    return render_template("history.html")

@app.route("/problem", methods=['GET', 'POST'])
def problem():
    if not user.isConnected():
        return redirect(url_for('login'))
    if request.method == 'POST':
        pass# TODO
        return render_template("problem.html",signaled=True)
    else:
        return render_template("problem.html")


@app.route('/logout')
def logout():
    user.disconnectUser()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True) # debug : server will reload itself on code changes
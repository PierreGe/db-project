# -*- coding: utf-8 -*-

from flask import Flask,render_template, g, session, redirect, url_for, escape, request
import os
import user
from models import Database
import config

app = Flask(__name__)
app.secret_key = os.urandom(24)

def get_db():
    if not hasattr(g, '_db'):
        g._db = Database()
    return g._db


def require_login(func):
    """
    Simple decorator that requires the user to be logged in to display the view
    """
    def wrapper(*args, **kwargs):
        if not user.isConnected():
            return redirect(url_for('login') + '?next=' + request.path)
        return func(*args, **kwargs)
    wrapper.__name__ = "login_required_" + func.__name__
    return wrapper


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/sqltest")
def sqltest():
    res = "\n".join(
        "Bike [%d] %s" % (bike.id, bike.model) for bike in get_db().Bike.all())
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
    next_page = request.args['next'] if 'next' in request.args else url_for('index')
    if request.method == 'POST':
        if user.checkLoginPassword(request.form['inputUsername'],request.form['inputPassword']):
            user.connectUser(request.form['inputUsername'])
            return redirect(next_page)
        else:
            return render_template("login.html", loginFailure=True)
    else:
        return render_template("login.html", next=next_page)


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
    return render_template("station.html", station_list=get_db().Station.all())


@app.route("/trip")
@require_login
def trip():
    return render_template("trip.html")


@app.route("/history")
@require_login
def history():
    return render_template("history.html", trip_list=get_db().User.get(0).trips)


@app.route("/problem", methods=['GET', 'POST'])
def problem():
    if not user.isConnected():
        return redirect(url_for('login'))
    ctx = {'bike_list': get_db().Bike.all()}
    if request.method == 'POST':
        pass# TODO
        return render_template("problem.html",signaled=True, **ctx)
    else:
        return render_template("problem.html", **ctx)


@app.route('/logout')
def logout():
    user.disconnectUser()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=config.DEBUG) # debug : server will reload itself on code changes

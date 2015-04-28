# -*- coding: utf-8 -*-

from flask import Flask,render_template, g, session, redirect, url_for, escape, request, make_response
import os
from user import current_user, connect_user, disconnect_user
from models import Database
from datetime import timedelta
import config
from apputils import get_db
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

def require_login(func):
    """
    Simple decorator that requires the user to be logged in to display the view
    """
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for('login') + '?next=' + request.path)
        return func(*args, **kwargs)
    wrapper.__name__ = "login_required_" + func.__name__
    return wrapper


@app.template_filter('plur')
def pluralize(number, singular='', plural='s'):
    """Template filter to pluralize a suffix according to a number"""
    if number == 1:
        return singular
    else:
        return plural


@app.context_processor
def user_processor():
    return {'user': current_user()}


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route("/")
def index():
    return render_template("dashboard.html" if current_user() else "home.html")


@app.route('/session_status')
def session_status():
    if current_user():
        return 'Logged in as %s' % escape(current_user().id)
    return 'You are not logged in'


@app.route('/login', methods=['GET', 'POST'])
def login():
    next_page = request.args['next'] if 'next' in request.args else url_for('index')
    if request.method == 'POST':
        try:
            user = get_db().User.get(int(request.form['userId']))
            if user.auth(request.form['userPassword']):
                connect_user(user)
                return redirect(next_page)
        except KeyError:
            pass
        return render_template("login.html", loginFailure=True)
    else:
        return render_template("login.html", next=next_page)


@app.route('/subscription', methods=['POST'])
def subscription():
    if current_user():
        current_user().renew()
        return redirect(url_for('index'))
    else:
        new_user = get_db().User.create(
            password=request.form['userPassword'],
            card=request.form['userBankData'])
        connect_user(new_user)
        current_user().renew() # nouvel abonnement
        return render_template("welcome.html", user=new_user)

@app.route('/subscription', methods=['GET'])
def subscription_form():
    return render_template("subscription.html")


@app.route("/station")
def station():
    return render_template("station.html", station_list=get_db().Station.all())


@app.route("/map_station_popup/<int:station_id>")
def station_popup(station_id):
    ctx = {'station': get_db().Station.get(station_id)}
    return render_template("map_station_popup.html", **ctx)


@app.route("/trip")
@require_login
def trip():
    return render_template("trip.html")


@app.route("/history")
@require_login
def history():
    return render_template("history.html", trip_list=current_user().trips)


@app.route("/problem", methods=['GET', 'POST'])
@require_login
def problem():
    # ctx must be created after db update
    if request.method == 'POST':
        villoId = int(request.form['villo'])
        bike = get_db().Bike.get(villoId)
        bike.updateUsable(False)
        ctx = {'bike_list': get_db().Bike.allUsable()}
        ctx['signaled'] = True
    else:
        ctx = {'bike_list': get_db().Bike.allUsable()}
    return render_template("problem.html", **ctx)

@app.route("/billing", methods=['POST'])
@require_login
def billing_post():
    starting = current_user().expire_date - datetime.timedelta(days=(365))
    detail = ""
    detail += "# Abonnement \nCarte 1 an : 32.6 euros \n# Voyages \n"
    for trip in current_user().trips:
        if trip.departure_date > starting:
            detail += "De "+trip.departure_station.name+" ("+str(trip.departure_date)+") à "+trip.arrival_station.name+" ("+str(trip.arrival_date)+ ") : " + str(trip.price()) + "\n"
    response = make_response(detail)
    response.headers["Content-Disposition"] = "attachment; filename=facture-details.md"
    return response

@app.route("/billing", methods=['GET'])
@require_login
def billing():
    starting = current_user().expire_date - datetime.timedelta(days=(365))
    periodeFact = (starting.strftime("%d-%m-%Y"), str(current_user().expire_date.strftime("%d-%m-%Y")))
    AllTrip = current_user().trips
    billedTrip = []
    total = 32.60
    for trip in AllTrip:
        if trip.arrival_station:
            if trip.departure_date > starting:
                if trip.price():
                    billedTrip.append(trip)
                    total += trip.price()
    return render_template("billing.html",periodeBilling = periodeFact, totalBilled=str(total)+" euros", trip_list=billedTrip)


@app.route('/logout')
def logout():
    disconnect_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(
        debug=config.DEBUG, 
        host=config.WEB_ADDRESS, 
        port=config.WEB_PORT) # debug : server will reload itself on code changes

# -*- coding: utf-8 -*-

from flask import (
    Flask, render_template, g, session, redirect, url_for, escape, request, 
    make_response, flash
)
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

@app.route('/sqltest')
def sqltest():
    connect_user(get_db().User.get(0))
    return current_user().newUniqueRFID()

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
        F = request.form
        new_user = get_db().User.create(
            password=F['userPassword'],
            card=F['userBankData'],
            firstname=F['userFirstName'],
            lastname=F['userLastName'],
            phone_number=F['userPhone'],
            address="%s,%s %s %s %s" % (F['userStreet'], F['userNumber'], F['userPostalCode'], F['userCity'], F['userCountry']),
            rfid= get_db().User.newUniqueRFID())
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

@app.route("/drop/<int:station_id>")
@require_login
def drop_bike(station_id):
    trip = current_user().current_trip
    try:
        station = get_db().Station.get(station_id)
    except KeyError:
        flash("Station %d inconnue", "warning")
        return redirect("/")
    if not trip:
        flash("Vous n'avez pas de location en cours", "danger")
    else:
        trip.arrival_station_id = station_id
        trip.arrival_date = datetime.datetime.now()
        trip.update()
        flash(u"Vous avez déposé votre vélo à la station %s" % station.name, "success")
    return redirect("/")

@app.route("/rent/<int:station_id>")
@require_login
def station_detail(station_id):
    user = current_user()
    try:
        station = get_db().Station.get(station_id)
    except KeyError:
        flash("Station %d inconnue", "warning")
        return redirect("/station")
    return render_template("rent.html", station=station)


@app.route("/rent/<int:station_id>/bike/<int:bike_id>")
@require_login
def rent_bike(station_id, bike_id):
    user = current_user()
    try:
        station = get_db().Station.get(station_id)
    except KeyError:
        flash("Station %d inconnue", "warning")
        return redirect("/station")
    try:
        bike = get_db().Bike.get(bike_id)
    except KeyError:
        flash("Villo %d inconnu", "warning")
        return redirect("/rent/%d" % (station_id))
    newTrip = get_db().Trip.create(
        user_id=user.id, bike_id=bike.id, 
        departure_station_id=station.id, departure_date=datetime.datetime.now())
    flash("Vous avez pris le villo %d" % (bike.id), 'success')
    return redirect("/")

@app.route("/history", methods=['POST'])
@require_login
def history_post():
    detail = "Date de debut;Date de fin;Station de depart;Station de fin\n"
    for trip in current_user().trips :
        detail+= str(trip.departure_date) + ";" + str(trip.arrival_date) + ";" + trip.arrival_station.name + ";" + trip.departure_station.name + "\n"
    response = make_response(detail)
    response.headers["Content-Disposition"] = "attachment; filename=trajet-details.csv"
    return response


@app.route("/history", methods=['GET'])
@require_login
def history():
    minkm = sum([float(x.distance()) for x in current_user().trips])
    def month_displayname(date):
        months = ["Janvier", "Fevrier", "Mars", "Avril", "Mai", "Juin", "Juillet", "Aout", "Spetembre", "Octobre", "Novembre", "Decembre"]
        return "%s %d" % (months[date.month-1], date.year)

    trip_list = current_user().trips
    trips_by_month = []
    if len(trip_list) > 0:
        trips_by_month = [
            (month_displayname(trip_list[0].departure_date), [trip_list[0]])
        ]
        for trip in trip_list[1:]:
            name = month_displayname(trip.departure_date)
            if name == trips_by_month[-1][0]:
                trips_by_month[-1][1].append(trip)
            else:
                trips_by_month.append((name, [trip]))
    return render_template("history.html",minimum_km=minkm, trips_by_month=trips_by_month)


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
    detail = "Type;Prix;Date de debut;Date de fin;Station de depart;Station de fin\n"
    detail += "Abonnement;32.6;"+starting.strftime("%d-%m-%Y")+";" +str(current_user().expire_date.strftime("%d-%m-%Y"))+ ";None;None\n"
    for trip in current_user().trips :
        if trip.departure_date > starting:
            detail+= "Trajet;" +str(trip.price()) + ";" +str(trip.departure_date) + ";" + str(trip.arrival_date) + ";" + trip.arrival_station.name + ";" + trip.departure_station.name + "\n"
            #detail += "De "+trip.departure_station.name+" ("+str(trip.departure_date)+") à "+trip.arrival_station.name+" ("+str(trip.arrival_date)+ ") : " + str(trip.price()) + "\n"
    response = make_response(detail)
    response.headers["Content-Disposition"] = "attachment; filename=facture-details.csv"
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
    return render_template("billing.html",periodeBilling = periodeFact, totalBilled=str(total), trip_list=billedTrip)


@app.route('/logout')
def logout():
    disconnect_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(
        debug=config.DEBUG, 
        host=config.WEB_ADDRESS, 
        port=config.WEB_PORT) # debug : server will reload itself on code changes

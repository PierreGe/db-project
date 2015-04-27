# -*- coding: utf-8 -*-

from flask import Flask,render_template, g, session, redirect, url_for, escape, request, make_response
import os
from user import current_user, connect_user, disconnect_user
from models import Database
import config
from apputils import get_db

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


@app.context_processor
def user_processor():
    return {'user': current_user()}


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


@app.route('/inscription', methods=['POST'])
def inscription():
    new_user = get_db().User.create(
        password=request.form['userPassword'],
        card=request.form['userBankData'])
    connect_user(new_user)
    return render_template("welcome.html", user=new_user)

@app.route('/inscription', methods=['GET'])
def inscription_form():
    return render_template("inscription.html")


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
    ctx = {'bike_list': get_db().Bike.allUsable()}
    if request.method == 'POST':
        villoId = int(request.form['villo'])
        bike = get_db().Bike.get(villoId)
        bike.updateUsable(False)
        ctx['signaled'] = True
    return render_template("problem.html", **ctx)

@app.route("/billing", methods=['POST'])
@require_login
def billing_post():
    detail = ""
    detail += "# Abonnement \nCarte 1 an : 32.6 euros \n# Voyages \n"
    for trip in current_user().trips:
        detail += "De "+trip.departure_station.name+" ("+str(trip.departure_date)+") à "+trip.arrival_station.name+" ("+str(trip.arrival_date)+ ") : " + str(trip.price()) + "\n"
    response = make_response(detail)
    response.headers["Content-Disposition"] = "attachment; filename=facture-details.md"
    return response

@app.route("/billing", methods=['GET'])
@require_login
def billing():
    AllTrip = current_user().trips
    billedTrip = []
    total = 32.60
    for trip in AllTrip:
        if trip.arrival_station:
            # Periode de facturation
            if trip.price():
                billedTrip.append(trip)
                total += trip.price()
    return render_template("billing.html",totalBilled=total, trip_list=billedTrip)


@app.route('/logout')
def logout():
    disconnect_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(
        debug=config.DEBUG, 
        host=config.WEB_ADDRESS, 
        port=config.WEB_PORT) # debug : server will reload itself on code changes

__author__ = 'pierre'


from flask import Flask,render_template, g, session, redirect, url_for, escape, request
import sqlite3
import os

DATABASE = 'test.sqlite'

app = Flask(__name__)
app.secret_key = os.urandom(24)


def connect_to_database():
    return sqlite3.connect(DATABASE)

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/sqltest")
def sqltest():
    q = query_db("SELECT * FROM bike")
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
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    return 'You are not logged in'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Check user ID and password here (champs : inputPassword)
        if request.form['inputUsername'] == "admin" and request.form['inputPassword'] =="admin":
            #success
            session['username'] = request.form['inputUsername']
            return redirect(url_for('index'))
        else:
            return render_template("login.html",loginFailure=True)
            #failure
    else:
        return render_template("login.html")

@app.route('/inscription', methods=['GET', 'POST'])
def inscription():
    if request.method == 'POST':
        # Check user ID and password here (champs : inputPassword)
        if request.form['inputUsername'] == "admin" and request.form['inputPassword'] =="admin":
            #success
            session['username'] = request.form['inputUsername']
            return redirect(url_for('index'))
        else:
            return render_template("login.html",loginFailure=True)
            #failure
    else:
        return render_template("inscription.html")

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True) # debug : server will reload itself on code changes
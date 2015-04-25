__author__ = 'pierre'


from flask import Flask, g
import sqlite3

from config import DATABASE

app = Flask(__name__)

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

@app.route("/")
def hello():
    q = query_db("SELECT * FROM bike")
    res = ""
    for i in q:
        for j in i:
            res += str(j)
        res += "\n"
    return "RAW BIKE LIST : " + res


if __name__ == "__main__":
    app.run(debug=True) # debug : server will reload itself on code changes
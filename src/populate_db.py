# -*- coding: utf-8 -*-

from csv import DictReader
from sqlite3 import Connection
from sys import stdout
from datetime import datetime

def create_tables(db, create_file="createDB.sql"):
    # Create tables using createDB.sql 
    # (sqlite3 module cannot run multiple statements at once)
    creator = open(create_file).read().split(';')[:-1]
    for create_table in creator:
        db.execute(create_table)

# Sanitize an argument for insertion
def sanitize(arg):
    if isinstance(arg, str) or isinstance(arg, unicode):
        return arg.replace('"', '\\"')
    elif isinstance(arg, datetime):
        return arg.strftime("%Y-%m-%dT%H:%M:%S")
    else:
        return str(arg)

# Sanitize all arguments
safe = lambda *args: tuple(map(sanitize, args))

def info(msg):
    stdout.write("\r%-80s" % msg)
    stdout.flush()

def insert_bikes(db, input_file="data/villos.csv"):
    q = lambda id, entry_date, model, usable: 'INSERT INTO bike (id,entry_date,model,usable) VALUES ("%s","%s","%s","%s")' % safe(id, entry_date, model, usable)
    for bike in DictReader(open("data/villos.csv"), delimiter=';'):
        db.execute(q(
            id=int(bike['nume\xcc\x81ro']),
            entry_date=(bike['mise en service']),
            usable=(bike['fonctionne'] == 'True'),
            model=bike['mode\xcc\x80le']))
        info("Inserted bike " + bike['nume\xcc\x81ro'])
    print

def insert_stations(db, input_file="data/stations.csv"):
    q = lambda id, payment, capacity, latitude, longitude, name: 'INSERT INTO station (id,payment,capacity,latitude,longitude,name) VALUES ("%s","%s","%s","%s","%s","%s")' % safe(id, payment, capacity, latitude, longitude, name)
    for station in DictReader(open("data/stations.csv"), delimiter=';'):
        db.execute(q(
            id=int(station['nume\xcc\x81ro']),
            payment=(station['borne de paiement'] == 'True'),
            capacity=int(station['capacite\xcc\x81']),
            latitude=float(station['coordonne\xcc\x81e X']),
            longitude=float(station['coordonne\xcc\x81e Y']),
            name=(station['nom'])))
        info("Inserted station " + station['nom'])
    print

# table (str) -> query for count of all elements in this table (str)
count_all = lambda table: "SELECT COUNT(*) FROM %s;" % (table)

def initDB(db_file=":memory:"):
    dbconnect = Connection(db_file)
    dbconnect.isolation_level = None
    db = dbconnect.cursor()

    create_tables(db)

    insert_bikes(db)
    assert db.execute(count_all('bike')).next()[0] == 2000

    insert_stations(db)
    assert db.execute(count_all('station')).next()[0] == 179

    dbconnect.close()

if __name__ == "__main__":
    initDB()

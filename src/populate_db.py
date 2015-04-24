# -*- coding: utf-8 -*-

from csv import DictReader
from sqlite3 import Connection

db = Connection("test.sqlite")

insert_bike = lambda id, entry_date, model, usable: "INSERT INTO bike (id,entry_date,model,usable) VALUES (%d,'%s','%s','%s');" % (id, entry_date, model, usable)
insert_station = lambda id, payment, capacity, latitude, longitude, name: "INSERT INTO station (id, payment, capacity, latitude, longitude, name) VALUES (%d,'%s','%d','%f', '%f', '%s');" % (id, payment, capacity, latitude, longitude, name)



for bike in DictReader(open("data/villos.csv"), delimiter=';'):
    query = insert_bike(
        id=int(bike['nume\xcc\x81ro']),
        entry_date=(bike['mise en service']),
        usable=(bike['fonctionne'] == 'True'),
        model=bike['mode\xcc\x80le'])
    res = db.execute(query)
    print query, [row for row in res]

for station in DictReader(open("data/stations.csv"), delimiter=';'):
    query = insert_station(
        id=int(station['nume\xcc\x81ro']),
        payment=(station['borne de paiement'] == 'True'),
        capacity=int(station['capacite\xcc\x81']),
        latitude=float(station['coordonne\xcc\x81e X']),
        longitude=float(station['coordonne\xcc\x81e Y']),
        name=(station['nom']))
    res = db.execute(query)
    print query, [row for row in res]


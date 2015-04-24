# -*- coding: utf-8 -*-

from csv import DictReader
from sqlite3 import Connection

db = Connection("test.sqlite")

insert_bike = lambda id, entry_date, model, usable: "INSERT INTO bike (id,entry_date,model,usable) VALUES (%d,'%s','%s','%s');" % (id, entry_date, model, usable)

for bike in DictReader(open("data/villos.csv"), delimiter=';'):
    query = insert_bike(
        id=int(bike['nume\xcc\x81ro']),
        entry_date=(bike['mise en service']),
        usable=(bike['fonctionne'] == 'True'),
        model=bike['mode\xcc\x80le'])
    res = db.execute(query)
    print query, [row for row in res]

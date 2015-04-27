# -*- coding: utf-8 -*-

from csv import DictReader
from sqlite3 import Connection
from sys import stdout, argv
from datetime import datetime
import xml.etree.ElementTree as ET

from dbutils import hash_password, sanitize

def create_tables(db, create_file="createDB.sql"):
    # Create tables using createDB.sql 
    # (sqlite3 module cannot run multiple statements at once)
    creator = open(create_file).read().split(';')[:-1]
    for create_table in creator:
        db.execute(create_table)

# Sanitize all arguments
safe = lambda *args: tuple(map(sanitize, args))

# Parse date in std format
parse_date = lambda datestr: datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S")

def insert_bikes(db, input_file="data/villos.csv"):
    q = 'INSERT INTO bike (id,entry_date,model,usable) VALUES (?,?,?,?)'
    bikelist = (
        (
            int(bike['nume\xcc\x81ro']),
            bike['mise en service'],
            bike['fonctionne'] == 'True',
            bike['mode\xcc\x80le']
        ) for bike in DictReader(open(input_file), delimiter=';')
    )
    with db:
        db.executemany(q, bikelist)

def insert_stations(db, input_file="data/stations.csv"):
    q = 'INSERT INTO station (id,payment,capacity,latitude,longitude,name) VALUES (?,?,?,?,?,?)'
    stationlist = (
        (
            int(station['nume\xcc\x81ro']),
            station['borne de paiement'] == 'True',
            int(station['capacite\xcc\x81']),
            float(station['coordonne\xcc\x81e Y']),
            float(station['coordonne\xcc\x81e X']),
            station['nom']
        ) for station in DictReader(open(input_file), delimiter=';')
    )
    with db:
        db.executemany(q, stationlist)

def insert_users(db, input_file="data/users.xml"):
    users_dom = ET.parse(input_file).getroot()
    users, subscribers = [], []

    for subscriber in users_dom.find('subscribers'):
        userdata = {f.tag: f.text for f in subscriber if f.tag != "address"}
        addr = subscriber.find('address')
        addrstr = ' '.join(map(
            lambda x: addr.find(x).text, 
            ('street', 'number', 'cp', 'city')))
        users.append((
            int(userdata['userID']),
            userdata['password'],
            userdata['card'],
            userdata['expiryDate']
        ))
        subscribers.append((
            int(userdata['userID']),
            userdata['RFID'],
            userdata['firstname'],
            userdata['lastname'],
            addrstr,
            userdata['phone']
        ))
    
    for tmpuser in users_dom.find('temporaryUsers'):
        userdata = {f.tag: f.text for f in tmpuser}
        users.append((
            int(userdata['userID']),
            userdata['password'],
            userdata['card'],
            userdata['expiryDate'],
        ))

    with db:
        db.executemany(
            'INSERT INTO user (id,password,card,expire_date) VALUES (?,?,?,?)',
            users)
        db.executemany(
            'INSERT INTO subscriber (user_id,rfid,firstname,lastname,address,phone_number) VALUES (?,?,?,?,?,?)',
            subscribers)

def insert_trips(db, input_file="data/trips.csv"):
    assert db.execute('INSERT INTO user (password,card,expire_date) VALUES ("%s","","")' % (hash_password('admin'))).rowcount == 1
    res = db.execute('SELECT id FROM user WHERE password="%s" AND expire_date=""' % (hash_password('admin')))
    admin_id = res.next()[0]

    def extract_trip(trip):
        if trip['depart'] == 'None':
            trip['depart'] = trip['arrive\xcc\x81e']
        if trip['heure de\xcc\x81part'] == 'None':
            trip['heure de\xcc\x81part'] = trip['heure arrive\xcc\x81e']
        if trip['utilisateur'] == 'None':
            trip['utilisateur'] = int(admin_id)
        return (
            int(trip['depart']),
            trip['heure de\xcc\x81part'],
            int(trip['arrive\xcc\x81e']) if trip['arrive\xcc\x81e'] != 'None' else None,
            trip['heure arrive\xcc\x81e'] if trip['heure arrive\xcc\x81e'] != 'None' else None,
            trip['utilisateur'],
            int(trip['ve\xcc\x81lo'])
        )

    q = 'INSERT INTO trip (departure_station_id,departure_date,arrival_station_id,arrival_date,user_id,bike_id) VALUES (?,?,?,?,?,?)'
    with db:
        db.executemany(q, 
            map(extract_trip, DictReader(open(input_file), delimiter=';')))

def initDB(db_file=":memory:"):
    def do_nothing(*args):
        pass

    TABLES = [
        ('bike', 'data/villos.csv', insert_bikes, 2000), 
        ('station', 'data/stations.csv', insert_stations, 179),
        ('user', 'data/users.xml', insert_users, 1096),
        ('subscriber', 'data/users.xml', do_nothing, 552),
        ('trip', 'data/trips.csv', insert_trips, 46717),
    ]

    db = Connection(db_file)

    def count_all(table):
        return db.execute("SELECT COUNT(*) FROM %s;" % (table)).next()[0]

    create_tables(db)
    for table, input_file, insert, expected_rows in TABLES:
        insert(db, input_file)
        assert count_all(table) == expected_rows, "Should insert %d rows in '%s'" % (expected_rows, table)

if __name__ == "__main__":
    from config import DATABASE
    initDB(argv[1] if len(argv) > 1 else DATABASE)

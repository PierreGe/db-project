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

def info(msg):
    stdout.write("\r%-80s" % msg)
    stdout.flush()

def insert_bikes(db, input_file="data/villos.csv"):
    q = lambda id, entry_date, model, usable: 'INSERT INTO bike (id,entry_date,model,usable) VALUES (%s,%s,%s,%s)' % safe(id, entry_date, model, usable)
    for bike in DictReader(open(input_file), delimiter=';'):
        assert 1 == db.execute(q(
            id=int(bike['nume\xcc\x81ro']),
            entry_date=(bike['mise en service']),
            usable=(bike['fonctionne'] == 'True'),
            model=bike['mode\xcc\x80le'])).rowcount
        info("Inserted bike " + bike['nume\xcc\x81ro'])
    print

def insert_stations(db, input_file="data/stations.csv"):
    q = lambda id, payment, capacity, latitude, longitude, name: 'INSERT INTO station (id,payment,capacity,latitude,longitude,name) VALUES (%s,%s,%s,%s,%s,%s)' % safe(id, payment, capacity, latitude, longitude, name)
    for station in DictReader(open(input_file), delimiter=';'):
        assert 1 == db.execute(q(
            id=int(station['nume\xcc\x81ro']),
            payment=(station['borne de paiement'] == 'True'),
            capacity=int(station['capacite\xcc\x81']),
            latitude=float(station['coordonne\xcc\x81e X']),
            longitude=float(station['coordonne\xcc\x81e Y']),
            name=(station['nom']))).rowcount
        info("Inserted station " + station['nom'])
    print

def insert_users(db, input_file="data/users.xml"):
    users = ET.parse(input_file).getroot()
    # Insert user
    qu = lambda id, passwd, card, expire: 'INSERT INTO user (id,password,card,expire_date) VALUES (%s,%s,%s,%s)' % safe(id, hash_password(passwd), card, expire)
    # Insert subscriber
    qs = lambda id, rfid, firstname, lastname, address, phone_number: 'INSERT INTO subscriber (user_id,rfid,firstname,lastname,address,phone_number) VALUES (%s,%s,%s,%s,%s,%s)' % safe(id, rfid, firstname, lastname, address, phone_number)

    for subscriber in users.find('subscribers'):
        userdata = {f.tag: f.text for f in subscriber if f.tag != "address"}
        addr = subscriber.find('address')
        addrstr = ' '.join(map(
            lambda x: addr.find(x).text, 
            ('street', 'number', 'cp', 'city')))
        assert 1 == db.execute(qu(
            id=int(userdata['userID']),
            passwd=userdata['password'],
            card=userdata['card'],
            expire=parse_date(userdata['expiryDate']))).rowcount
        assert 1 == db.execute(qs(
            id=int(userdata['userID']),
            rfid=userdata['RFID'],
            firstname=userdata['firstname'],
            lastname=userdata['lastname'],
            address=addrstr,
            phone_number=userdata['phone'])).rowcount
        info(userdata['userID'] + " " + addrstr)
    print
    
    for tmpuser in users.find('temporaryUsers'):
        userdata = {f.tag: f.text for f in tmpuser}
        assert 1 == db.execute(qu(
            id=int(userdata['userID']),
            passwd=userdata['password'],
            expire=userdata['expiryDate'],
            card=userdata['card'])).rowcount
        info(userdata['userID'] + " " + userdata['expiryDate'])
    print

def insert_trips(db, input_file="data/trips.csv"):
    assert db.execute('INSERT INTO user (password,card,expire_date) VALUES ("%s","","")' % (hash_password('admin'))).rowcount == 1
    res = db.execute('SELECT id FROM user WHERE password="%s" AND expire_date=""' % (hash_password('admin')))
    admin_id = res.next()[0]

    q = lambda from_station, from_date, to_station, to_date, user, bike: 'INSERT INTO trip (departure_station_id,departure_date,arrival_station_id,arrival_date,user_id,bike_id) VALUES (%s,%s,%s,%s,%s,%s)' % safe(from_station, from_date, to_station, to_date, user, bike)
    for trip in DictReader(open(input_file), delimiter=';'):
        if trip['depart'] == 'None':
            trip['depart'] = trip['arrive\xcc\x81e']
        if trip['heure de\xcc\x81part'] == 'None':
            trip['heure de\xcc\x81part'] = trip['heure arrive\xcc\x81e']
        if trip['utilisateur'] == 'None':
            trip['utilisateur'] = int(admin_id)
        assert 1 == db.execute(q(
            from_station=int(trip['depart']),
            to_station=int(trip['arrive\xcc\x81e']) if trip['arrive\xcc\x81e'] != 'None' else None,
            from_date=parse_date(trip['heure de\xcc\x81part']),
            to_date=parse_date(trip['heure arrive\xcc\x81e']) if trip['heure arrive\xcc\x81e'] != 'None' else None,
            user=trip['utilisateur'],
            bike=int(trip['ve\xcc\x81lo']))).rowcount
        info("Trip [%s] %s -> %s" % (trip['depart'], trip['arrive\xcc\x81e'], trip['ve\xcc\x81lo']))
    print

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

    dbconnect = Connection(db_file)
    dbconnect.isolation_level = None
    db = dbconnect.cursor()

    def count_all(table):
        return db.execute("SELECT COUNT(*) FROM %s;" % (table)).next()[0]

    create_tables(db)
    for table, input_file, insert, expected_rows in TABLES:
        insert(db, input_file)
        assert count_all(table) == expected_rows, "Should insert %d rows in '%s'" % (expected_rows, table)

    dbconnect.close()

if __name__ == "__main__":
    from config import DATABASE
    initDB(argv[1] if len(argv) > 1 else DATABASE)

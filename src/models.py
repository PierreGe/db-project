"""
A minimalistic DAO for our database. Example:

    # DAO creation
    Trip = get_Trip(sqlite3.Connection("madb.sqlite"))

    # Get all objects
    Trip.all() -> [ <Trip ...>, ... ]
    
    # Get first trip
    trip = Trip.all()[0]

    # Get some attributes, possibly related objects
    trip.departure_date -> datetime(2012, 12, 21, 11, 11, 11)
    trip.departure_station -> <Station [42] PLACE DE L'EVEQUE>
    trip.bike -> <Bike id=83>
    trip.user -> <User id=27>
"""

import config
import sqlite3
from datetime import datetime, timedelta
from dbutils import hash_password
from populate_db import create_tables
from random import randint
import math

def datestr(date):
    return date.strftime("%Y-%m-%dT%H:%M:%S")

def parse_date(datestr):
    if isinstance(datestr, str) or isinstance(datestr, unicode):
        return datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S")
    elif isinstance(datestr, datetime):
        return datestr
    raise TypeError()

def memoize(method):
    name = '_retval_' + method.__name__
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, name):
            setattr(self, name, method(self, *args, **kwargs))
        return getattr(self, name)
    return wrapper

def fetch_first(cursor):
    """Return the very first value of the cursor (ex COUNTs)"""
    return cursor.next()[0]

def fetch_is_empty(cursor):
    if cursor.fetchone():
        return True
    return False

def fetch_one(as_class, cursor):
    """Return the first row of cursor cast to as_class"""
    values = cursor.next()
    return as_class(*values)

def fetch_all(as_class, cursor):
    """Like fetch_one, but on all rows of the cursor"""
    return [as_class(*row) for row in cursor]

default_or_db = lambda db: sqlite3.Connection(config.DATABASE) if db is None else db

def _get_Model(db):
    """Return an abstract base model bound to given database"""

    class Model(object):
        columns = []

        def __iter__(self):
            return (getattr(self, col) for col in self.columns)

        def encode(self, obj):
            if isinstance(obj, datetime):
                return obj.strftime("%Y-%m-%dT%H:%M:%S")
            return obj

        def insert(self):
            query = 'INSERT INTO %s (%s) VALUES (%s)' % (
                    self.tablename(), 
                    ','.join(self.columns), 
                    ','.join(['?']*len(self.columns)))
            with db:
                db.execute(query, map(self.encode, self))
                if 'id' in self.columns:
                    self.id = fetch_first(
                        db.execute(
                            "SELECT last_insert_rowid() FROM %s" % 
                            self.tablename()))
            return self

        @classmethod
        def create(klass, *args, **kwargs):
            res = klass(*args, **kwargs)
            res.insert()
            return res

        @classmethod
        def tablename(klass):
            return klass.__name__.lower()

        @classmethod
        def cols(klass):
            return ','.join(klass.columns)

        @classmethod
        def all(klass):
            return fetch_all(
                klass,
                db.execute(
                    "SELECT %s FROM %s" % (klass.cols(), klass.tablename())))

        @classmethod
        def count(klass):
            return fetch_first(
                db.execute("SELECT COUNT(*) FROM %s" % klass.tablename()))

        def __repr__(self):
            id = self.id if self.id is not None else "?"
            return "<%s id=%s>" % (self.__class__.__name__, str(id))

    return Model

def get_Bike(db=None, superclass=None):
    """Get a Bike DAO with provided db"""
    db = default_or_db(db)
    if superclass is None:
        superclass = _get_Model(db)

    class Bike(superclass):
        columns = ['id', 'entry_date', 'model', 'usable']

        def __init__(self, id=None, entry_date=None, model="JCDECAUX2010", usable=True):
            self.id = int(id) if id is not None else None
            self.entry_date = parse_date(entry_date) if entry_date else datetime.now()
            self.model = str(model)
            self.usable = True if usable else False

        def update(self):
            with db:
                db.execute(
                    "UPDATE bike SET entry_date=?, model=?, usable=? WHERE id=?",
                    (datestr(self.entry_date), self.model, self.usable, self.id))

        def updateUsable(self,newValue):
            with db:
                db.execute(
                    "UPDATE bike SET usable=? WHERE id=?",
                    (newValue, self.id))
            self.usable = newValue

        @property
        @memoize
        def location(self):
            Station = get_Station(db, superclass)
            cursor = db.execute(
                """SELECT DISTINCT %s FROM station
                   INNER JOIN trip ON station.id=trip.arrival_station_id
                   WHERE bike_id=?
                   ORDER BY departure_date DESC""" % (Station.cols()),
                (self.id,))
            try:
                return fetch_one(Station, cursor)
            except StopIteration:
                return None

        @property
        def trips(self):
            Trip = get_Trip(db, superclass)
            return fetch_all(Trip, db.execute(
                "SELECT %s FROM trip WHERE bike_id=?" % Trip.cols(),
                (self.id,)))

        @classmethod
        def allUsable(klass):
            return fetch_all(klass, db.execute(
                "SELECT %s FROM %s WHERE usable=1" % (klass.cols(), klass.tablename())))


        @classmethod
        def allBroken(klass):
            return fetch_all(klass, db.execute(
                "SELECT %s FROM %s WHERE usable=0" % (klass.cols(), klass.tablename())))


        @classmethod
        def get(klass, id):
            try:
                return fetch_one(klass, db.execute(
                    "SELECT id,entry_date,model,usable FROM bike WHERE id=? LIMIT 1",
                    (id,)))
            except StopIteration:
                raise KeyError(id)

    return Bike

def get_User(db=None, superclass=None):
    """Get a User DAO with provided db"""
    db = default_or_db(db)
    if superclass is None:
        superclass = _get_Model(db)

    class User(superclass):
        columns = ['id', 'password', 'card', 'expire_date']

        def __init__(self, id=None, password_hash="", card="", expire_date=None, rfid=None, firstname=None, lastname=None, address_street=None,address_streenumber=None, address_zipcode=None, address_city=None,address_country=None, entry_date=None, phone_number=None, password=None,
                     ):
            self.id = int(id) if id is not None else None
            self.password = password_hash if password_hash else hash_password(password)
            self.card = card
            self.expire_date = parse_date(expire_date) if expire_date else None
            self.rfid = rfid
            self.address_street = address_street
            self.address_streenumber = None if address_streenumber is None else int(address_streenumber)
            self.address_zipcode = None if address_zipcode is None else int(address_zipcode)
            self.address_city = address_city
            self.address_country = address_country
            self.firstname, self.lastname = firstname, lastname
            self.entry_date = parse_date(entry_date) if entry_date else datestr(datetime.now())
            self.phone_number = phone_number

        def insert(self, *args, **kwargs):
            super(User, self).insert()
            if self.is_subscriber():
                with db:
                    db.execute(
                        "INSERT INTO subscriber (user_id,rfid,firstname,lastname,address_street,address_streenumber,address_zipcode,address_city,address_country,entry_date,phone_number) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                        map(self.encode, (self.id, self.rfid, self.firstname, self.lastname, self.address_street,self.address_streenumber,self.address_zipcode, self.address_city, self.address_country, self.entry_date, self.phone_number)))

        def is_subscriber(self):
            return (
                self.address_city is not None and
                self.rfid is not None and
                self.firstname is not None and
                self.lastname is not None)

        def niceName(self):
            if self.firstname and self.lastname:
                return str(self.firstname).capitalize() + " " + str(self.lastname).capitalize()
            return str(self.id)

        def update(self):
            with db:
                db.execute(
                    "UPDATE user SET password=?, card=?, expire_date=? WHERE id=?",
                    map(self.encode, (self.password, self.card, self.expire_date, self.id)))

        def is_admin(self):
            return self.expire_date is None

        def auth(self, password):
            return hash_password(password) == self.password

        def renew(self):
            newEndDate = datetime.now() + timedelta(days=(365))
            newEndDate = newEndDate.replace(second=0, microsecond=0)
            with db:
                db.execute(
                    "UPDATE user SET expire_date=? WHERE id=?",
                    (datestr(newEndDate), self.id))
            self.expire_date = newEndDate

        @property
        def active_trips(self):
            assert self.is_admin()
            Trip = get_Trip(db, superclass)
            try:
                return fetch_all(Trip, db.execute(
                    'SELECT %s FROM trip WHERE user_id=? AND arrival_station_id IS NULL' % Trip.cols(),
                    (self.id,)))
            except StopIteration:
                return None

        @property
        def current_trip(self):
            """
            Return the user's current trip (a trip with no arrival_station),
            or None if the user has no current trip
            """
            Trip = get_Trip(db, superclass)
            try:
                return fetch_one(Trip, db.execute(
                    'SELECT %s FROM trip WHERE user_id=? AND arrival_station_id IS NULL LIMIT 1' % Trip.cols(),
                    (self.id,)))
            except StopIteration:
                return None

        def has_bike(self, bike_id):
            """Return true if the User is using designated bike at the moment"""
            return fetch_first(db.execute(
                "SELECT COUNT(bike_id) FROM trip WHERE user_id=? AND bike_id=? AND arrival_station_id IS NULL",
                (self.id, bike_id))) == 1

        @staticmethod
        def newUniqueRFID():
            digitNumber = 20
            rfid = str(randint(10**(digitNumber-1), (10**digitNumber)-1))
            while fetch_is_empty(db.execute("SELECT rfid FROM subscriber WHERE rfid=?",(rfid,))) :
                rfid = str(randint(10**(digitNumber-1), (10**digitNumber)-1))
            return rfid


        @property
        def expired(self, when=None):
            if when is None:
                when = datetime.now()
            return self.expire_date and self.expire_date < parse_date(when)

        @property
        def trips(self):
            Trip = get_Trip(db, superclass)
            return fetch_all(Trip, db.execute(
                "SELECT %s FROM %s WHERE user_id=? ORDER BY departure_date DESC" % (Trip.cols(), Trip.tablename()), 
                (self.id,)))

        def billable_trips(self, from_time=None, to_time=None):
            """Return all billable trips for this user for given period"""
            if to_time is None:
                to_time = datetime.now()
            if from_time is None:
                from_time = to_time - timedelta(days=365)

            from_time, to_time = parse_date(from_time), parse_date(to_time)

            Trip = get_Trip(db, superclass)
            Q = """
            SELECT %s FROM %s
            WHERE ?<=departure_date AND
                  arrival_date<=? AND
                  user_id=? AND
                  strftime('%%s',arrival_date)-strftime('%%s',departure_date) >= 1800
            """ % (Trip.cols(), Trip.tablename())
            args = map(self.encode, (from_time, to_time, self.id))
            return fetch_all(Trip, db.execute(Q, args))

        @classmethod
        def get(klass, id):
            return fetch_one(klass, db.execute(
                """SELECT id, password, card, expire_date, rfid,firstname, lastname,
                          address_street, address_streenumber, address_zipcode, address_city,
                          address_country, entry_date, phone_number
                   FROM user
                   LEFT JOIN subscriber ON user.id=subscriber.user_id
                   WHERE id=? LIMIT 1""",(id,)))

    return User

def get_Trip(db=None, superclass=None):
    """Get a Trip DAO with provided db"""
    db = default_or_db(db)
    if superclass is None:
        superclass = _get_Model(db)

    class Trip(superclass):
        columns = [
            'user_id', 'bike_id',
            'departure_station_id', 'departure_date',
            'arrival_station_id', 'arrival_date',
        ]

        def __init__(self, user_id, bike_id, departure_station_id, departure_date=None, arrival_station_id=None, arrival_date=None):
            self.departure_station_id = int(departure_station_id)
            self.departure_date = parse_date(departure_date) if departure_date else datetime.now()
            self.user_id = int(user_id)
            self.bike_id = int(bike_id)
            self.arrival_station_id = int(arrival_station_id) if arrival_station_id is not None else None
            self.arrival_date = parse_date(arrival_date) if arrival_date else None

        @property
        def user(self):
            User = get_User(db, superclass)
            return User.get(self.user_id)

        @property
        @memoize
        def bike(self):
            Bike = get_Bike(db, superclass)
            return Bike.get(self.bike_id)

        @property
        def finished(self):
            return self.arrival_date != None

        def is_insertion(self):
            """
            Return True if the trip is a bike insertion
            (admin putting a bike in the system)
            """
            return (
                self.departure_date == self.arrival_date and
                self.departure_station_id == self.arrival_station_id and
                self.user.expire_date is None)

        def duration(self, current_time=None):
            """
            :param current_time:
            :return: des secondes
            """
            if self.finished:
                current_time = self.arrival_date
            elif current_time is None:
                current_time = datetime.now()
            return parse_date(current_time) - self.departure_date

        def price(self):
            durationTrip = int(self.duration().total_seconds())
            price = 0
            durationTrip -= 60*30 # 30 minute gratuite
            if durationTrip > 0: # 30-60 minute
                durationTrip -= 60*30
                price+= 0.5
            if durationTrip > 0: # 30-60 minute
                durationTrip -= 60*30
                price+= 1
            #while durationTrip > 0: # par 30 minutes en plus
            #    durationTrip -= 60*30
            #    price+= 2
            price += 2 * (math.ceil(durationTrip/(60*30.)))
            return price

        def distance(self):
            """
            :return: des kilometres
            """
            if self.departure_station_id == self.arrival_station_id or not self.finished:
                return 0.
            query = """
            SELECT geodistance(s1.latitude,s1.longitude,s2.latitude,s2.longitude)
            FROM trip
            INNER JOIN station AS s1 ON s1.id=trip.departure_station_id,
                       station AS s2 ON s2.id=trip.arrival_station_id
            WHERE trip.departure_date=? AND
                  trip.user_id=? AND
                  trip.bike_id=?
            """
            res = fetch_first(db.execute(query, map(self.encode, 
                (self.departure_date, self.user_id, self.bike_id))))
            return round(res, 2)

        @property
        def departure_station(self):
            Station = get_Station(db, superclass)
            return Station.get(self.departure_station_id)

        @property
        def arrival_station(self):
            if self.finished:
                Station = get_Station(db, superclass)
                return Station.get(self.arrival_station_id)
            return None

        @property
        def id(self):
            return (self.user_id, self.bike_id, self.departure_date)

        def update(self):
            with db:
                db.execute(
                    "UPDATE trip SET arrival_station_id=?, arrival_date=? WHERE user_id=? AND bike_id=? AND departure_date=?",
                    (self.arrival_station_id, self.encode(self.arrival_date), self.user_id, self.bike_id, self.encode(self.departure_date)))

    return Trip

def get_Station(db=None, superclass=None):
    """Get a Station DAO with provided db"""
    db = default_or_db(db)
    if superclass is None:
        superclass = _get_Model(db)

    class Station(superclass):
        columns = ['payment', 'capacity', 'latitude', 'longitude', 'name', 'id']

        CountBikesQuery = '''SELECT COUNT(bike_id) FROM (
            SELECT user_id,bike_id,arrival_station_id,MAX(departure_date)
            FROM trip
            GROUP BY bike_id) 
        JOIN bike ON bike.id=bike_id 
        WHERE arrival_station_id=?'''
        BikesQuery = '''SELECT %s FROM (
            SELECT bike_id,arrival_station_id,MAX(departure_date)
            FROM trip GROUP BY bike_id)
        JOIN bike ON bike.id=bike_id WHERE arrival_station_id=?''' % get_Bike(db, superclass).cols()

        def __init__(self, payment, capacity, latitude, longitude, name, id=None):
            self.latitude, self.longitude = float(latitude), float(longitude)
            self.name = str(name)
            self.payment = True if payment else False
            self.capacity = int(capacity)
            self.id = int(id) if id is not None else None

        def __repr__(self):
            id = str(self.id) if self.id is not None else "?"
            return "<Station [%s] %s>" % (id, self.name)

        @property
        @memoize
        def available_bikes(self):
            """
            Return the number of all bikes at this station
            """
            return fetch_first(db.execute(
                self.CountBikesQuery + ' AND bike.usable=?', (self.id, True)))

        @property
        @memoize
        def broken_bikes(self):
            """
            Return the number of unusable bikes at this station
            """
            return fetch_first(db.execute(
                self.CountBikesQuery + ' AND bike.usable=?', (self.id, False)))

        @property
        @memoize
        def all_bikes(self):
            """
            Return the total number of bikes at this station
            """
            return fetch_first(db.execute(self.CountBikesQuery, (self.id,)))
        
        @property
        @memoize
        def bikes(self):
            """
            Return the list of bikes stopped at this station
            """
            Bike = get_Bike(db, superclass)
            return fetch_all(Bike, db.execute(self.BikesQuery, (self.id,)))

        @property
        def free_slots(self):
            return self.capacity - self.all_bikes

        @classmethod
        def get(klass, id):
            try:
                return fetch_one(klass, db.execute(
                "SELECT %s FROM %s WHERE id=? LIMIT 1" % (klass.cols(), klass.tablename()), 
                (id,)))
            except StopIteration:
                raise KeyError(id)

    return Station

class Database(object):
    def __init__(self, connection=None):
        connection = default_or_db(connection)
        create_tables(connection)
        connection.enable_load_extension(True)
        connection.load_extension("./geodistance")
        connection.enable_load_extension(False)
        base_model = _get_Model(connection)
        self.Trip = get_Trip(connection, base_model)
        self.Bike = get_Bike(connection, base_model)
        self.User = get_User(connection, base_model)
        self.Station = get_Station(connection, base_model)

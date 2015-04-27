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
from datetime import datetime
from dbutils import hash_password

def datestr(date):
    return date.strftime("%Y-%m-%dT%H:%M:%S")

def parse_date(datestr):
    if isinstance(datestr, str) or isinstance(datestr, unicode):
        return datetime.strptime(datestr, "%Y-%m-%dT%H:%M:%S")
    elif isinstance(datestr, datetime):
        return datestr
    raise TypeError()

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
                    cursor = db.execute("SELECT last_insert_rowid() FROM %s" % self.tablename())
                    self.id = int(cursor.next()[0])
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
            cursor = db.execute("SELECT %s FROM %s" % (klass.cols(), klass.tablename()))
            return [klass(*row) for row in cursor]

        @classmethod
        def count(klass):
            cursor = db.execute("SELECT COUNT(*) FROM %s" % klass.tablename())
            return cursor.next()[0]

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

        @property
        def location(self):
            cursor = db.execute(
                "SELECT arrival_station_id FROM trip WHERE bike_id=? ORDER BY departure_date DESC LIMIT 1",
                (self.id,))
            try:
                res = cursor.next()[0]
            except StopIteration:
                return None
            if res is not None:
                Station = get_Station(db, superclass)
                return Station.get(res)

        @property
        def trips(self):
            Trip = get_Trip(db, superclass)
            cursor = db.execute(
                "SELECT %s FROM trip WHERE bike_id=?" % Trip.cols(),
                (self.id,))

        @classmethod
        def get(klass, id):
            cursor = db.execute(
                "SELECT id,entry_date,model,usable FROM bike WHERE id=? LIMIT 1", 
                (id,))
            try:
                row = cursor.next()
            except StopIteration:
                raise KeyError(id)
            return klass(*row)

    return Bike

def get_User(db=None, superclass=None):
    """Get a User DAO with provided db"""
    db = default_or_db(db)
    if superclass is None:
        superclass = _get_Model(db)

    class User(superclass):
        columns = ['id', 'password', 'card', 'expire_date']

        def __init__(self, id=None, password_hash="", card="", expire_date=None, password=None):
            self.id = int(id) if id is not None else None
            self.password = password_hash if password_hash else hash_password(password)
            self.card = card
            self.expire_date = parse_date(expire_date) if expire_date else None

        def update(self):
            with db:
                db.execute(
                    "UPDATE user SET password=?, card=?, expire_date=? WHERE id=?",
                    (self.password, self.card, self.expire_date, self.id))

        def is_admin(self):
            return self.expire_date is None

        def auth(self, password):
            return hash_password(password) == self.password

        @property
        def expired(self, when=None):
            if when is None:
                when = datetime.now()
            return self.expire_date and self.expire_date < parse_date(when)

        @property
        def trips(self):
            Trip = get_Trip(db, superclass)
            cursor = db.execute(
                "SELECT %s FROM %s WHERE user_id=? ORDER BY departure_date DESC" % (Trip.cols(), Trip.tablename()), 
                (self.id,))
            return [Trip(*row) for row in cursor]

        @classmethod
        def get(klass, id):
            cursor = db.execute(
                "SELECT id,password,card,expire_date FROM user WHERE id=? LIMIT 1", 
                (id,))
            try:
                row = cursor.next()
            except StopIteration:
                raise KeyError(id)
            return klass(*row)

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
        def bike(self):
            Bike = get_Bike(db, superclass)
            return Bike.get(self.bike_id)

        @property
        def finished(self):
            return self.arrival_date != None

        def duration(self, current_time=None):
            if self.finished:
                current_time = self.arrival_date
            elif current_time is None:
                current_time = datetime.now()
            return parse_date(current_time) - self.departure_date

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

    return Trip

def get_Station(db=None, superclass=None):
    """Get a Station DAO with provided db"""
    db = default_or_db(db)
    if superclass is None:
        superclass = _get_Model(db)

    class Station(superclass):
        columns = ['payment', 'capacity', 'latitude', 'longitude', 'name', 'id']

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
        def available_bikes(self):
            """
            Return the number of available bikes at this station
            """
            query = "SELECT COUNT(bike_id) FROM (SELECT user_id,bike_id,arrival_station_id,MAX(departure_date) FROM trip GROUP BY bike_id) WHERE arrival_station_id=?"
            cursor = db.execute(query, (self.id,))
            return cursor.next()[0]
        
        @property
        def bikes(self):
            """
            Return the list of bikes stopped at this station
            """
            Bike = get_Bike(db, superclass)
            query = "SELECT %s FROM (SELECT bike_id,arrival_station_id,MAX(departure_date) FROM trip GROUP BY bike_id) JOIN bike ON bike.id=bike_id WHERE arrival_station_id=?"
            cursor = db.execute(query%Bike.cols(), (self.id,))
            return [Bike(*row) for row in cursor]

        @classmethod
        def get(klass, id):
            cursor = db.execute(
                "SELECT %s FROM %s WHERE id=? LIMIT 1" % (klass.cols(), klass.tablename()), 
                (id,))
            try:
                row = cursor.next()
            except StopIteration:
                raise KeyError(id)
            return klass(*row)

    return Station

class Database(object):
    def __init__(self, connection=None):
        connection = default_or_db(connection)
        base_model = _get_Model(connection)
        self.Trip = get_Trip(connection, base_model)
        self.Bike = get_Bike(connection, base_model)
        self.User = get_User(connection, base_model)
        self.Station = get_Station(connection, base_model)

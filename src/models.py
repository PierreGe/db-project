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

class Model(object):
    def __repr__(self):
        return "<%s id=%s>" % (self.__class__.__name__, self._get_pk_repr())

def get_Bike(db=None):
    """Get a Bike DAO with provided db"""
    db = default_or_db(db)

    class Bike(Model):
        _get_pk_repr = lambda self: self.id if self.id else "?"

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

        def create(self):
            with db:
                db.execute(
                    "INSERT INTO bike (id,entry_date,model,usable) VALUES (?,?,?,?)",
                    (self.id, datestr(self.entry_date), self.model, self.usable))

        @classmethod
        def all(klass):
            cursor = db.execute("SELECT id,entry_date,model,usable FROM bike")
            return [klass(*row) for row in cursor]

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

        @classmethod
        def count(klass):
            cursor = db.execute("SELECT COUNT(*) FROM bike")
            return cursor.next()[0]

    return Bike

def get_User(db=None):
    """Get a User DAO with provided db"""
    db = default_or_db(db)

    class User(Model):
        _get_pk_repr = lambda self: self.id if self.id else "?"

        def __init__(self, id=None, password_hash="", card="", expire_date=None, password=None):
            self.id = int(id) if id is not None else None
            self.password_hash = password_hash if password_hash else hash_password(password)
            self.card = card
            self.expire_date = parse_date(expire_date) if expire_date else None

        def create(self):
            with db:
                db.execute(
                    "INSERT INTO user (id,password,card,expire_date) VALUES (?,?,?,?)",
                    (self.id, self.password_hash, self.card, self.expire_date))

        def update(self):
            with db:
                db.execute(
                    "UPDATE user SET password=?, card=?, expire_date=? WHERE id=?",
                    (self.password_hash, self.card, self.expire_date, self.id))

        def is_admin(self):
            return self.expire_date is None

        def auth(self, password):
            return hash_password(password) == self.password_hash

        @classmethod
        def all(klass):
            cursor = db.execute("SELECT id,password,card,expire_date FROM user")
            return [klass(*row) for row in cursor]

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

        @classmethod
        def count(klass):
            cursor = db.execute("SELECT COUNT(*) FROM user")
            return cursor.next()[0]

    return User

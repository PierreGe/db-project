from models import sqlite3, Database, parse_date
from populate_db import create_tables
from datetime import datetime, timedelta

db = None

def setup_function(*args):
    global db
    db = Database(sqlite3.Connection(':memory:'))


def teardown_function(*args):
    global db
    db = None


def test_create_bike():
    assert len(db.Bike.all()) == 0
    db.Bike.create()
    assert len(db.Bike.all()) == 1


def test_repr_bike():
    assert repr(db.Bike()) == "<Bike id=?>"
    db.Bike.create()
    assert repr(db.Bike.get(1)) == "<Bike id=1>"


def test_bike_count():
    assert db.Bike.count() == 0
    db.Bike.create()
    assert db.Bike.count() == 1


def test_create_user():
    assert len(db.User.all()) == 0
    u = db.User.create(password="hello")
    assert len(db.User.all()) == 1
    assert not u.is_subscriber()


def test_subscriber():
    u = db.User.create(
            password="AZERTY",
            card="123",
            firstname="Alain",
            lastname="Terieur",
            address_street="rue des Heliotropes",
            address_streenumber= "124",
            address_zipcode="6700",
            address_city= "Bxl",
            address_country="Luxembourg",
            entry_date= "2010-01-01T10:00:00",
            phone_number="0491234567",
            rfid= "123"
        )
    assert u.is_subscriber()
    assert u.rfid == "123"
    assert u.firstname == "Alain"
    assert u.lastname == "Terieur"
    assert u.address_street == "rue des Heliotropes"
    assert u.address_streenumber == "124"
    assert u.address_zipcode == "6700"
    assert u.address_city == "Bxl"
    assert u.address_country == "Luxembourg"
    assert u.phone_number == "0491234567"
    
    u = db.User.get(u.id)
    assert u.is_subscriber()
    assert u.rfid == "123"
    assert u.firstname == "Alain"
    assert u.lastname == "Terieur"
    assert u.address_street == "rue des Heliotropes"
    assert u.address_streenumber == "124"
    assert u.address_zipcode == "6700"
    assert u.address_city == "Bxl"
    assert u.address_country == "Luxembourg"
    assert u.phone_number == "0491234567"


def test_create_user_with_id():
    user = db.User(password="42", id=42)
    user.insert()
    assert db.User.get(42)


def test_repr_user():
    assert repr(db.User(password="hello")) == "<User id=?>"
    db.User(password="hello").insert()
    assert repr(db.User.get(1)) == "<User id=1>"


def test_auth_user():
    titou = db.User(password="cafedeca")
    assert titou.auth("cafedeca")
    assert not titou.auth("lalala")


def test_isadmin_user():
    admin = db.User(password="admin")
    n00b = db.User(password="n00b", expire_date="2014-08-25T12:14:23")
    assert admin.is_admin()
    assert not n00b.is_admin()


def test_trip_duration():
    t = datetime(2012, 12, 21, 11, 11, 11)
    trip = db.Trip(0, 0, 0, departure_date=t)
    assert not trip.finished
    assert trip.duration(t + timedelta(seconds=20)).total_seconds() == 20


def test_autoassign_id():
    u = db.User(password="123")
    assert u.id is None
    u.insert()
    assert u.id == 1


def test_insert_trip():
    u = db.User.create(password="Hello")
    b = db.Bike.create(model="mytest")
    assert b.location is None

    s1 = db.Station.create(
        latitude=50.3245, longitude=4.0326, 
        name="db.Station 1", capacity=42, payment=True)
    s2 = db.Station.create(
        latitude=50.3245, longitude=4.0325,
        name="db.Station 2", capacity=42, payment=True)
    from_date, to_date = "2015-07-12T10:10:10", "2015-07-12T11:10:10"

    t = db.Trip.create(
        departure_station_id=s1.id, arrival_station_id=s2.id,
        departure_date=from_date, arrival_date=to_date,
        user_id=u.id, bike_id=b.id
    )

    # Refresh for location memoizing
    b = db.Bike.get(b.id)

    assert t.user.auth("Hello")
    assert t.bike.model == "mytest"
    assert b.location.name == "db.Station 2"


def test_station_available_bikes():
    u = db.User.create(password="Hello")
    b = db.Bike.create(model="mytest")
    s1 = db.Station.create(
        latitude=50.3245, longitude=4.0326, 
        name="db.Station 1", capacity=42, payment=True)
    s2 = db.Station.create(
        latitude=50.3245, longitude=4.0325,
        name="db.Station 2", capacity=42, payment=True)
    from_date, to_date = "2015-07-12T10:10:10", "2015-07-12T11:10:10"

    assert s2.available_bikes == 0
    assert s1.available_bikes == 0

    t = db.Trip.create(
        departure_station_id=s1.id, arrival_station_id=s2.id,
        departure_date=from_date, arrival_date=to_date,
        user_id=u.id, bike_id=b.id
    )

    # Refresh memoized values
    s1, s2 = db.Station.get(1), db.Station.get(2)

    assert s2.available_bikes == 1
    assert [bike.id for bike in s2.bikes] == [b.id]
    assert s1.available_bikes == 0
    assert s1.bikes == []

    from_date, to_date = "2015-07-12T20:10:10", "2015-07-12T21:10:10"
    t = db.Trip.create(
        departure_station_id=s2.id, arrival_station_id=s1.id,
        departure_date=from_date, arrival_date=to_date,
        user_id=u.id, bike_id=b.id
    )

    # Refresh memoized values
    s1, s2 = db.Station.get(1), db.Station.get(2)

    assert s2.available_bikes == 0
    assert s2.bikes == []
    assert s1.available_bikes == 1
    assert [bike.id for bike in s1.bikes] == [b.id]

    bike.usable = False
    bike.update()
    assert s1.broken_bikes == 1


def test_trip_price():
    """
    Location:
     *  0-30 min: gratuit
     * 30-60 min: 0.5
     * 60-90 min: 1.5
     * 90+ min: 1.5 + 2*(min-90)/30
    """
    from_date, to_date = "2015-07-12T10:10:10", "2015-07-12T10:20:10"

    t = db.Trip(
        user_id=42, bike_id=42, departure_station_id=42,
        departure_date=from_date, arrival_date=to_date)
    assert t.duration().total_seconds() == 600
    assert t.price() == 0

    t.arrival_date = parse_date("2015-07-12T10:50:10")
    assert t.duration().total_seconds() == 2400
    assert t.price() == 0.5

    t.arrival_date = parse_date("2015-07-12T11:20:10")
    assert t.duration().total_seconds() == 4200
    assert t.price() == 1.5

    t.arrival_date = parse_date("2015-07-12T11:50:10")
    assert t.duration().total_seconds() == 6000
    assert t.price() == 3.5


def test_user_current_trip():
    u = db.User.create(password="Hello")
    assert u.current_trip is None
    assert db.Trip.count() == 0

    b = db.Bike.create(model="mytest")
    s1 = db.Station.create(
        latitude=50.3245, longitude=4.0325, 
        name="db.Station 1", capacity=42, payment=True)
    from_date = "2015-07-12T10:10:10"
    t = db.Trip.create(
        departure_station_id=s1.id,
        departure_date=from_date,
        user_id=u.id, bike_id=b.id
    )

    assert db.Trip.count() == 1
    assert u.current_trip is not None
    assert u.current_trip.bike_id == b.id
    assert u.current_trip.departure_station_id == s1.id
    assert u.current_trip.arrival_station_id is None
    assert u.has_bike(b.id)

# Run tests if no py.test
if __name__ == "__main__":
    env = dict(globals())
    for name,val in env.iteritems():
        if callable(val) and name.startswith('test_'):
            setup_function()
            val()
            teardown_function()


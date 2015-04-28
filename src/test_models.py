from models import sqlite3, get_Bike, get_User, get_Trip, get_Station, parse_date
from populate_db import create_tables
from datetime import datetime, timedelta

Bike, User, Trip, Station = None, None, None, None


def setup_function(*args):
    global Bike, User, Trip, Station
    db = sqlite3.Connection(':memory:')
    create_tables(db)
    Bike = get_Bike(db)
    User = get_User(db)
    Trip = get_Trip(db)
    Station = get_Station(db)


def teardown_function(*args):
    global Bike, User, Trip, Station
    Bike, User, Trip, Station = None, None, None, None


def test_create_bike():
    assert len(Bike.all()) == 0
    Bike.create()
    assert len(Bike.all()) == 1


def test_repr_bike():
    assert repr(Bike()) == "<Bike id=?>"
    Bike.create()
    assert repr(Bike.get(1)) == "<Bike id=1>"


def test_bike_count():
    assert Bike.count() == 0
    Bike.create()
    assert Bike.count() == 1


def test_create_user():
    assert len(User.all()) == 0
    u = User.create(password="hello")
    assert len(User.all()) == 1
    assert not u.is_subscriber()


def test_subscriber():
    u = User.create(address="123 rue des Heliotropes",
        password="hello", rfid="123", 
        firstname="Alain", lastname="Terieur", 
        phone_number="0491234567")
    assert u.is_subscriber()
    assert u.rfid == "123"
    assert u.firstname == "Alain"
    assert u.lastname == "Terieur"
    assert u.address == "123 rue des Heliotropes"
    assert u.phone_number == "0491234567"
    
    u = User.get(u.id)
    assert u.is_subscriber()
    assert u.rfid == "123"
    assert u.firstname == "Alain"
    assert u.lastname == "Terieur"
    assert u.address == "123 rue des Heliotropes"
    assert u.phone_number == "0491234567"


def test_create_user_with_id():
    user = User(password="42", id=42)
    user.insert()
    assert User.get(42)


def test_repr_user():
    assert repr(User(password="hello")) == "<User id=?>"
    User(password="hello").insert()
    assert repr(User.get(1)) == "<User id=1>"


def test_auth_user():
    titou = User(password="cafedeca")
    assert titou.auth("cafedeca")
    assert not titou.auth("lalala")


def test_isadmin_user():
    admin = User(password="admin")
    n00b = User(password="n00b", expire_date="2014-08-25T12:14:23")
    assert admin.is_admin()
    assert not n00b.is_admin()


def test_trip_duration():
    t = datetime(2012, 12, 21, 11, 11, 11)
    trip = Trip(0, 0, 0, departure_date=t)
    assert not trip.finished
    assert trip.duration(t + timedelta(seconds=20)).total_seconds() == 20


def test_autoassign_id():
    u = User(password="123")
    assert u.id is None
    u.insert()
    assert u.id == 1


def test_insert_trip():
    u = User.create(password="Hello")
    b = Bike.create(model="mytest")
    assert b.location is None

    s1 = Station.create(
        latitude=50.3245, longitude=4.0325, 
        name="Station 1", capacity=42, payment=True)
    s2 = Station.create(
        latitude=50.3245, longitude=4.0325,
        name="Station 2", capacity=42, payment=True)
    from_date, to_date = "2015-07-12T10:10:10", "2015-07-12T11:10:10"

    t = Trip.create(
        departure_station_id=s1.id, arrival_station_id=s2.id,
        departure_date=from_date, arrival_date=to_date,
        user_id=u.id, bike_id=b.id
    )

    assert t.user.auth("Hello")
    assert t.bike.model == "mytest"
    assert b.location.name == "Station 2"


def test_station_available_bikes():
    u = User.create(password="Hello")
    b = Bike.create(model="mytest")
    s1 = Station.create(
        latitude=50.3245, longitude=4.0325, 
        name="Station 1", capacity=42, payment=True)
    s2 = Station.create(
        latitude=50.3245, longitude=4.0325,
        name="Station 2", capacity=42, payment=True)
    from_date, to_date = "2015-07-12T10:10:10", "2015-07-12T11:10:10"

    assert s2.available_bikes == 0
    assert s1.available_bikes == 0

    t = Trip.create(
        departure_station_id=s1.id, arrival_station_id=s2.id,
        departure_date=from_date, arrival_date=to_date,
        user_id=u.id, bike_id=b.id
    )

    # Refresh memoized values
    s1, s2 = Station.get(1), Station.get(2)

    assert s2.available_bikes == 1
    assert [bike.id for bike in s2.bikes] == [b.id]
    assert s1.available_bikes == 0
    assert s1.bikes == []

    from_date, to_date = "2015-07-12T20:10:10", "2015-07-12T21:10:10"
    t = Trip.create(
        departure_station_id=s2.id, arrival_station_id=s1.id,
        departure_date=from_date, arrival_date=to_date,
        user_id=u.id, bike_id=b.id
    )

    # Refresh memoized values
    s1, s2 = Station.get(1), Station.get(2)

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

    t = Trip(
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

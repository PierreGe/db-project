from models import sqlite3, get_Bike, get_User, get_Trip, get_Station
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
    User(password="hello").insert()
    assert len(User.all()) == 1


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

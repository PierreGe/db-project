from models import Database
from datetime import datetime, timedelta
import sqlite3
import pytest

db = None

def setup_function(*args):
    global db
    db = Database(sqlite3.Connection(':memory:'))


def teardown_function(*args):
    global db
    db = None


def test_user_same_id():
    db.User.create(id=1, password="42")
    with pytest.raises(sqlite3.IntegrityError):
        db.User.create(id=1, password="32")


def test_bike_same_id():
    db.Bike.create(id=1)
    with pytest.raises(sqlite3.IntegrityError):
        db.Bike.create(id=1)


def test_station_same_id():
    db.Station.create(id=1, latitude=1, longitude=2, name="A", payment=True, capacity=10)
    with pytest.raises(sqlite3.IntegrityError):
        db.Station.create(id=1, latitude=3, longitude=4, name="A", payment=True, capacity=10)


def test_station_same_coordinates():
    db.Station.create(id=1, latitude=1, longitude=2, name="A", payment=True, capacity=10)
    with pytest.raises(sqlite3.IntegrityError):
        db.Station.create(id=2, latitude=1, longitude=2, name="A", payment=True, capacity=10)


def test_station_incorrect_coordinates():
    with pytest.raises(sqlite3.IntegrityError):
        db.Station.create(id=1, latitude=1000, longitude=200, name="A", payment=True, capacity=10)


def test_station_negative_capacity():
    with pytest.raises(sqlite3.IntegrityError):
        db.Station.create(id=1, latitude=1, longitude=2, name="A", payment=True, capacity=-1)


def test_trip_inexistant_foreignkey():
    with pytest.raises(sqlite3.IntegrityError):
        db.Trip.create(user_id=11, bike_id=22, departure_station_id=33)


def test_trip_arrival_before_departure():
    t = datetime(2012, 12, 21, 11, 11, 11)
    u = db.User.create(password="qsd")
    s = db.Station.create(id=1, latitude=1, longitude=2, name="A", payment=True, capacity=10)
    b = db.Bike.create()
    with pytest.raises(sqlite3.IntegrityError):
        db.Trip.create(
            user_id=u.id, bike_id=b.id, 
            departure_station_id=s.id, departure_date=t,
            arrival_station_id=s.id, arrival_date=t-timedelta(seconds=42))


def test_trip_primary_key():
    t = datetime(2012, 12, 21, 11, 11, 11)
    u = db.User.create(password="qsd")
    s = db.Station.create(id=1, latitude=1, longitude=2, name="A", payment=True, capacity=10)
    b = db.Bike.create()
    db.Trip.create(
        user_id=u.id, bike_id=b.id, 
        departure_station_id=s.id, departure_date=t,
        arrival_station_id=s.id, arrival_date=t+timedelta(seconds=42))
    with pytest.raises(sqlite3.IntegrityError):
        db.Trip.create(
            user_id=u.id, bike_id=b.id, 
            departure_station_id=s.id, departure_date=t,
            arrival_station_id=s.id, arrival_date=t+timedelta(seconds=42))


def test_subscriber_unique_rfid():
    db.User.create(password="123", rfid="123", firstname="a", lastname="a", address_street="rue des Heliotropes",
            address_streenumber= 124,
            address_zipcode=6700,
            address_city= "Bxl",
            address_country="Luxembourg",)
    with pytest.raises(sqlite3.IntegrityError):
        db.User.create(password="123", rfid="123", firstname="a", lastname="a", address_street="rue des Heliotropes",
            address_streenumber= 124,
            address_zipcode=6700,
            address_city= "Bxl",
            address_country="Luxembourg",)

from models import Database
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

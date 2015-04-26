from models import sqlite3, get_Bike, get_User
from populate_db import create_tables


Bike = None
User = None


def setup_function(*args):
    global Bike, User
    db = sqlite3.Connection(':memory:')
    create_tables(db)
    Bike = get_Bike(db)
    User = get_User(db)


def teardown_function(*args):
    global Bike, User
    Bike = None
    User = None


def test_create_bike():
    assert len(Bike.all()) == 0
    Bike().create()
    assert len(Bike.all()) == 1


def test_repr_bike():
    assert repr(Bike()) == "<Bike id=?>"
    Bike().create()
    assert repr(Bike.get(1)) == "<Bike id=1>"


def test_bike_count():
    assert Bike.count() == 0
    Bike().create()
    assert Bike.count() == 1


def test_create_user():
    assert len(User.all()) == 0
    User(password="hello").create()
    assert len(User.all()) == 1


def test_create_user_with_id():
    user = User(password="42", id=42)
    user.create()
    assert User.get(42)


def test_repr_user():
    assert repr(User(password="hello")) == "<User id=?>"
    User(password="hello").create()
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

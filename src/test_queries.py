# -*- coding: utf-8 -*-

from populate_db import (
    create_tables, 
    insert_bikes, 
    insert_users,
    insert_stations, 
    insert_trips,
    Connection
)
from models import Database, fetch_all
from datetime import datetime, timedelta

def load_query(i):
    """Load SQL without comments from queries/r<i>.sql"""
    return ''.join(filter(
        lambda line: not line.strip().startswith("--"),
        open("queries/r%d.sql" % i)))

def exec_query(q):
    print q
    res = fetch_all(lambda *args: args, conn.execute(q))
    print res
    return res

def insert_fixtures(conn):
    db = Database(conn)

    # Time base
    t = lambda **args: datetime(2012, 12, 21, 11, 11, 11) + timedelta(**args)

    Admin = db.User.create(id=0, expire_date=None, password="admin")

    # A, B, C: Registred user, B and C in Ixelles
    A = db.User.create(id=1, expire_date=t(days=365),
        password="a", rfid="123456789",
        firstname="A", lastname="A",
        address_street="Rue du soleil", address_streenumber=12,
        address_zipcode=1070, address_city="Bruxelles", address_country="Belgique")
    B = db.User.create(id=2, expire_date=t(days=237),
        password="b", rfid="456789123",
        firstname="B", lastname="B",
        address_street="Chaussee de Boondael", address_streenumber=87,
        address_zipcode=1050, address_city="Bruxelles", address_country="Belgique")
    C = db.User.create(id=3, expire_date=t(days=344),
        password="c", rfid="789123456",
        firstname="C", lastname="C",
        address_street="Avenue de l'Universite", address_streenumber=537,
        address_zipcode=1050, address_city="Bruxelles", address_country="Belgique")

    # D, E: Temporary users
    D = db.User.create(password="d", expire_date=t(days=1))
    E = db.User.create(password="e", expire_date=t(days=5))

    # 5 bikes
    Bikes = [db.Bike.create() for i in range(5)]

    # 3 stations, including Flagey
    Flagey = db.Station.create(name="FLAGEY",
        latitude=50.8279234774, longitude=4.37191500367,
        payment=True, capacity=25)
    ULB = db.Station.create(name="ULB",
        latitude=50.8125663191, longitude=4.37914601751,
        payment=True, capacity=27)
    Arsenal = db.Station.create(name="ARSENAL",
        latitude=50.8265178652, longitude=4.39705753109,
        payment=True, capacity=25)
    Eloy = db.Station.create(name="ELOY",
        latitude=50.8362457584, longitude=4.32609149836,
        payment=True, capacity=25)

    # All bikes initially in Flagey by admin
    for bike in Bikes:
        db.Trip.create(
            user_id=Admin.id, bike_id=bike.id,
            departure_station_id=Flagey.id, departure_date=t(seconds=0),
            arrival_station_id=Flagey.id, arrival_date=t(seconds=0))

    # B: Flagey -> ULB, villo1
    db.Trip.create(
        user_id=B.id, bike_id=Bikes[0].id,
        departure_station_id=Flagey.id, departure_date=t(seconds=1),
        arrival_station_id=ULB.id, arrival_date=t(seconds=1200))

    # A: Flagey -> ULB, villo2
    db.Trip.create(
        user_id=A.id, bike_id=Bikes[1].id,
        departure_station_id=Flagey.id, departure_date=t(seconds=54000),
        arrival_station_id=ULB.id, arrival_date=t(seconds=58000))

    # E: ULB -> Arsenal, villo5 [DISCONTINUOUS TRIP !]
    db.Trip.create(
        user_id=E.id, bike_id=Bikes[4].id,
        departure_station_id=ULB.id, departure_date=t(days=1),
        arrival_station_id=Arsenal.id, arrival_date=t(days=1, seconds=1200))

    # E: Arsenal -> Eloy, villo5
    db.Trip.create(
        user_id=E.id, bike_id=Bikes[4].id,
        departure_station_id=Arsenal.id, departure_date=t(days=1, seconds=20000),
        arrival_station_id=Eloy.id, arrival_date=t(days=1, seconds=24000))

    # B: ULB -> Arsenal, villo1
    db.Trip.create(
        user_id=B.id, bike_id=Bikes[0].id,
        departure_station_id=ULB.id, departure_date=t(days=2),
        arrival_station_id=Arsenal.id, arrival_date=t(days=2, seconds=1200))

    # B: Flagey -> Eloy, villo 4
    db.Trip.create(
        user_id=B.id, bike_id=Bikes[3].id,
        departure_station_id=Flagey.id, departure_date=t(days=2, seconds=40000),
        arrival_station_id=Eloy.id, arrival_date=t(days=2, seconds=43800))

    # D: ULB -> Arsenal, villo2
    db.Trip.create(
        user_id=D.id, bike_id=Bikes[1].id,
        departure_station_id=ULB.id, departure_date=t(days=3),
        arrival_station_id=Arsenal.id, arrival_date=t(days=3, seconds=1200))

    # C: Eloy -> ... en cours, villo 4
    db.Trip.create(
        user_id=C.id, bike_id=Bikes[3].id,
        departure_station_id=Eloy.id, departure_date=t(days=3))

    # E: Eloy -> ... en cours, villo 5
    db.Trip.create(
        user_id=E.id, bike_id=Bikes[4].id,
        departure_station_id=Arsenal.id, departure_date=t(days=3, seconds=1200))

    # A: Flagey -> ULB, villo3
    db.Trip.create(
        user_id=A.id, bike_id=Bikes[2].id,
        departure_station_id=Flagey.id, departure_date=t(days=12, seconds=54000),
        arrival_station_id=ULB.id, arrival_date=t(days=12, seconds=58000))


conn = None
def setup_function(*args):
    global conn
    conn = Connection(':memory:')
    create_tables(conn)
    insert_fixtures(conn)

def teardown_function(*args):
    global conn
    conn = None

def test_expected_data():
    """Test fixtures content"""
    db = Database(conn)
    assert db.User.count() == 6
    assert db.Bike.count() == 5
    assert db.Station.count() == 4
    assert db.Trip.count() == 15

def test_r1():
    # B a loué un vélo à Flagey et habite Ixelles
    res = exec_query(load_query(1))
    assert res == [(2, "B", "B")]

def test_r2():
    # A, B et E ont 2 trajets chacun
    res = exec_query(load_query(2))
    assert res == [(1,), (2,), (5,)]

def test_r3():
    # A et B font tous les 2 le trajet Flagey -> ULB,
    # B et D font tous les 2 le trajet ULB -> Arsenal
    # B et E font tous les 2 le trajet ULB -> Arsenal
    # D et E font tous les 2 le trajet ULB -> Arsenal
    res = exec_query(load_query(3))
    assert res == [(1, 2), (2, 4), (2, 5), (4, 5)]

def test_r4():
    # Le villo 5 a un trajet discontinu
    res = exec_query(load_query(4))
    assert res == [(5,)]

def test_r5():
    res = exec_query(load_query(5))
    assert res == []

def test_r6():
    res = exec_query(load_query(6))
    assert res == []


# Run tests if no py.test
if __name__ == "__main__":
    env = dict(globals())
    for name,val in env.iteritems():
        if callable(val) and name.startswith('test_'):
            setup_function()
            val()
            teardown_function()

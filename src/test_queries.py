from populate_db import (
    create_tables, 
    insert_bikes, 
    insert_users,
    insert_stations, 
    insert_trips,
    Connection
)
from models import Database

def load_query(i):
    """Load SQL without comments from queries/r<i>.sql"""
    return ' '.join(filter(
        lambda line: not line.strip().startswith("--"),
        open("queries/r%d.sql" % i)))

conn = None

def setup_function(*args):
    global conn
    conn = Connection(':memory:')
    create_tables(conn)
    insert_bikes(conn, "queries/villos.csv")
    insert_stations(conn, "queries/stations.csv")
    insert_users(conn, "queries/users.xml")
    insert_trips(conn, "queries/trips.csv")

def teardown_function(*args):
    global conn
    conn = None

def test_expected_data():
    """Test fixtures content"""
    db = Database(conn)
    assert db.User.count() == 8
    assert db.Bike.count() == 11
    assert db.Station.count() == 4
    assert db.Trip.count() == 12

def test_r1():
    Q = load_query(1)
    res = [row for row in conn.execute(Q)]
    print Q
    print res
    assert res == [(1, "Mercedes", "BOURDON")]

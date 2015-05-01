CREATE TABLE IF NOT EXISTS station (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment BOOLEAN NOT NULL,
    capacity INTEGER NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    name VARCHAR(32) NOT NULL,
    UNIQUE(latitude, longitude)
);

CREATE TABLE IF NOT EXISTS bike (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_date VARCHAR(20) NOT NULL CHECK (entry_date IS strftime(entry_date)), -- SQLite has no DATETIME type, check que le format est bon
    model VARCHAR(32) NOT NULL,
    usable BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    password VARCHAR(64) NOT NULL,
    card VARCHAR(64) NOT NULL,
    expire_date VARCHAR(20) CHECK (expire_date IS strftime(expire_date))
);

CREATE TABLE IF NOT EXISTS subscriber (
    user_id INTEGER NOT NULL,
    rfid TEXT NOT NULL,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    address TEXT NOT NULL,
    phone_number VARCHAR(20) NOT NULL,

    FOREIGN KEY(user_id) REFERENCES user(id)
);

CREATE TABLE IF NOT EXISTS trip (
    departure_station_id INTEGER NOT NULL,
    departure_date VARCHAR(20) NOT NULL CHECK (departure_date IS strftime(departure_date)),

    arrival_station_id INTEGER,
    arrival_date VARCHAR(20) CHECK (arrival_date IS strftime(arrival_date)) , -- CHECK(datetime(arrival_date) > datetime(departure_date)) ?

    user_id INTEGER NOT NULL,
    bike_id INTEGER NOT NULL,

    FOREIGN KEY(departure_station_id) REFERENCES station(id),
    FOREIGN KEY(arrival_station_id) REFERENCES station(id),
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(bike_id) REFERENCES bike(id)
);

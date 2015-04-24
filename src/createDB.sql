CREATE TABLE IF NOT EXISTS station (
    id INTEGER PRIMARY KEY,
    payment BOOLEAN NOT NULL,
    capacity INTEGER NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    name VARCHAR(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS bike (
    id INTEGER PRIMARY KEY,
    entry_date VARCHAR(20) NOT NULL, -- SQLite has no DATETIME type
    model VARCHAR(32) NOT NULL,
    usable BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY,
    password VARCHAR(64) NOT NULL,
    card VARCHAR(64) NOT NULL,
    expire_date VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS trip (
    departure_station_id INTEGER,
    departure_date VARCHAR(20),

    arrival_station_id INTEGER,
    arrival_date VARCHAR(20),

    user_id INTEGER,
    bike_id INTEGER NOT NULL,

    FOREIGN KEY(departure_station_id) REFERENCES station(id),
    FOREIGN KEY(arrival_station_id) REFERENCES station(id),
    FOREIGN KEY(user_id) REFERENCES user(id),
    FOREIGN KEY(bike_id) REFERENCES bike(id)
);

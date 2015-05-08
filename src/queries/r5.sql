-- Les utilisateurs, la date d'inscription, le nombre total de trajet effectues,
-- la distance totale parcourue et la distance moyenne parcourue par trajet,
-- classes en fonction de la distance totale parcourue

--- Barycentre des stations villos: (50.84715777660501, 4.36273021165704)
--- Périmètre Ouest-Est de la terre à cette latitude: 70.2861540037661 km/°
--- Périmètre Nord-Sud de la terre: 110.94625213273459 km/° 
--- Distance entre 2 points (lat1,long1), (lat2,long2) -> 
---     SQRT((abs(lat2-lat1)*110)^2 + (abs(long2-long1)*70)^2)

SELECT   subscriber.firstname,
         subscriber.lastname,
         subscriber.entry_date,
         COUNT(trip.arrival_station_id) AS trip_count,
         SUM(geodistance(from_.latitude, from_.longitude, to_.latitude, to_.longitude)) AS total_km,
         AVG(geodistance(from_.latitude, from_.longitude, to_.latitude, to_.longitude)) AS avg_km
FROM     trip
INNER JOIN station AS from_ ON trip.departure_station_id = from_.id,
           station AS to_ ON trip.arrival_station_id = to_.id,
           subscriber ON trip.user_id = subscriber.user_id
WHERE    trip.arrival_station_id NOT null
GROUP BY subscriber.firstname,
         subscriber.lastname
ORDER BY count(trip.arrival_station_id);
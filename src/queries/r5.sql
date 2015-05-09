-- Les utilisateurs, la date d'inscription, le nombre total de trajet effectues,
-- la distance totale parcourue et la distance moyenne parcourue par trajet,
-- classes en fonction de la distance totale parcourue

--- Barycentre des stations villos: (50.84715777660501, 4.36273021165704)
--- Perimetre Ouest-Est de la terre a cette latitude: 70.2861540037661 km/[degre]
--- Perimetre Nord-Sud de la terre: 110.94625213273459 km/[degre]
--- Distance entre 2 points (lat1,long1), (lat2,long2) -> 
---     SQRT((abs(lat2-lat1)*110)^2 + (abs(long2-long1)*70)^2)

SELECT   subscriber.firstname,
         subscriber.lastname,
         subscriber.entry_date,
         COUNT(trip.arrival_station_id) AS trip_count,
         SUM(12309.070862300314*ABS(from_.latitude-to_.latitude)*ABS(from_.latitude-to_.latitude) + 4940.143444641126*ABS(from_.longitude-to_.longitude)*ABS(from_.longitude-to_.longitude)) AS km_squared
FROM     trip
INNER JOIN station AS from_ ON trip.departure_station_id = from_.id,
           station AS to_ ON trip.arrival_station_id = to_.id,
           subscriber ON trip.user_id = subscriber.user_id
WHERE    trip.arrival_station_id NOT null
GROUP BY subscriber.firstname,
         subscriber.lastname
ORDER BY count(trip.arrival_station_id);
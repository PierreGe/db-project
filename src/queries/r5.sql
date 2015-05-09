-- Les utilisateurs, la date d'inscription, le nombre total de trajet effectues,
-- la distance totale parcourue et la distance moyenne parcourue par trajet,
-- classes en fonction de la distance totale parcourue



-- SQLite ne dispose pas de fonction de la fonction sqrt(), ou de fonctions
-- trigonométriques, nécessaires au calcul de la distance sur terre. Nous avons
-- donc implémenté la formule de Haversine en tant qu'extension SQLite à
-- charger au démarrage, et qui intègre la fonction
-- geodistance(lat1,long1,lat2,long2) -> km à l'environnement SQL.

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
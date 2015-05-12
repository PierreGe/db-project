-- Les stations avec le nombre total de velos deposes dans cette station
-- (un meme velo peut-etre comptabilise plusieurs fois) et le nombre
-- d'utilisateurs differents ayant utilise la station et ce pour toutes les
-- stations ayant ete utilisees au moins 10 fois.



SELECT station.NAME,
       Count(trip.arrival_station_id),
       Count(DISTINCT trip.user_id)
FROM   station
       INNER JOIN trip
               ON trip.arrival_station_id = station.id
GROUP  BY station.id
HAVING Count(trip.arrival_station_id) >= 10; 

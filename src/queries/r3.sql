-- Les paires d'utilisateurs ayant fait un trajet identique

SELECT DISTINCT t1.user_id,
                t2.user_id
FROM   trip t1,
       trip t2
WHERE  t1.departure_station_id = t2.departure_station_id
       AND t1.arrival_station_id = t2.arrival_station_id
       AND t1.user_id < t2.user_id;
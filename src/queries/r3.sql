-- Les paires d'utilisateurs ayant fait un trajet identique

SELECT DISTINCT t1.user_id,
                t2.user_id
FROM   trip AS t1
       INNER JOIN trip AS t2
               ON t1.departure_station_id = t2.departure_station_id
                  AND t1.arrival_station_id = t2.arrival_station_id
                  AND t1.user_id < t2.user_id; 
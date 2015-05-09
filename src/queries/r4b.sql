--- Requete lente possible d'ecrire en algebre relationnel
SELECT DISTINCT t1.bike_id
FROM   trip t1, 
       trip t2 
WHERE  t1.bike_id = t2.bike_id 
       AND t1.arrival_station_id != t2.departure_station_id 
       AND t1.arrival_date < t2.departure_date 
       AND NOT EXISTS (SELECT t3.departure_station_id 
                       FROM   trip t3 
                       WHERE  t1.bike_id = t3.bike_id 
                              AND t1.arrival_date < t3.departure_date 
                              AND t3.departure_date < t2.departure_date); 
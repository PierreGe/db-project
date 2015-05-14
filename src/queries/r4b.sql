-- Les velos ayant deux trajets consecutifs disjoints (station de retour du
-- premier trajet differente de la station de depart du suivant)


SELECT DISTINCT t1.bike_id
FROM   trip AS t1
       INNER JOIN trip AS t2
               ON t1.bike_id = t2.bike_id
                  AND t1.arrival_date <= t2.departure_date
                  AND t1.arrival_station_id != t2.departure_station_id
       LEFT OUTER JOIN trip AS t3
                    ON t1.bike_id = t3.bike_id
                       AND t1.arrival_date < t3.arrival_date
                       AND t3.arrival_date < t2.departure_date
WHERE  t3.bike_id IS NULL;



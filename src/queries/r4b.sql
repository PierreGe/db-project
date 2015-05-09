SELECT DISTINCT t1.bike_id 
FROM   trip t1 
       INNER JOIN trip t2 
               ON t1.bike_id = t2.bike_id 
       LEFT JOIN trip AS t3 
              ON t1.bike_id = t3.bike_id 
                 AND t1.arrival_date < t3.departure_date 
                 AND t3.departure_date < t2.departure_date 
WHERE  t1.arrival_station_id != t1.departure_station_id 
       AND t1.arrival_station_id != t2.departure_station_id 
       AND t1.arrival_date < t2.departure_date 
       AND t3.bike_id IS NULL; 

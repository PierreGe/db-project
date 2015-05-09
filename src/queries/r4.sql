-- Les velos ayant deux trajets consecutifs disjoints (station de retour du
-- premier trajet differente de la station de depart du suivant)

--- Requete optimise et rapide mais avec un ORDER que l'on ne trouve pas en algebre relationnel
SELECT DISTINCT bike_id FROM (
    SELECT t1.bike_id AS bike_id,
           t1.arrival_station_id AS s1,
           t2.departure_station_id AS s2,
           t1.arrival_date AS arrival,
           t2.departure_date AS departure
    FROM trip t1
    INNER JOIN trip t2 ON t1.bike_id=t2.bike_id AND t1.arrival_date<t2.departure_date
    WHERE t1.arrival_date NOT NULL --AND t1.bike_id=5
    GROUP BY t2.departure_date
    ORDER BY t1.departure_date,t2.departure_date)
WHERE s1 != s2;

 
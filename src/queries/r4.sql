-- Les velos ayant deux trajets consecutifs disjoints (station de retour du
-- premier trajet differente de la station de depart du suivant)

-- Optimisation possible : Pour chaque velo, trier par date de depart et regarder 2 par 2, bon apres comme faire en sql ?

SELECT t1.bike_id AS bike_id
    FROM trip t1, trip t2
    WHERE t1.bike_id=t2.bike_id AND
          t1.arrival_station_id!=t2.departure_station_id AND
          t1.arrival_date < t2.departure_date AND
          NOT EXISTS (SELECT t3.departure_station_id FROM trip t3
           WHERE t1.bike_id=t3.bike_id AND
                 t1.arrival_date<t3.departure_date AND
                 t3.departure_date<t2.departure_date)
    GROUP BY t1.bike_id;

-- Les vélos ayant deux trajets consécutifs disjoints (station de retour du
-- premier trajet différente de la station de départ du suivant)}

SELECT * FROM trip trip1
    WHERE EXISTS (SELECT * FROM trip trip2
        WHERE trip1.user_id != trip2.user_id AND
              trip1.arrival_station_id NOT NULL AND
              trip1.departure_station_id = trip2.departure_station_id AND
              trip1.arrival_station_id = trip2.arrival_station_id);

-- Les utilisateurs, la date d'inscription, le nombre total de trajet effectues,
-- la distance totale parcourue et la distance moyenne parcourue par trajet,
-- classes en fonction de la distance totale parcourue


-- WARNING : math sur latitude, longitude

SELECT   subscriber.firstname,
         subscriber.lastname,
         subscriber.entry_date,
         Count(trip.arrival_station_id),
         departurestation.latitude,
         departurestation.longitude,
         arrivalstation.latitude,
         arrivalstation.longitude
FROM     subscriber,
         trip,
         station AS departurestation,
         station AS arrivalstation
WHERE    trip.arrival_station_id NOT null
AND      departurestation.id = trip.departure_station_id
AND      arrivalstation.id = trip.arrival_station_id
AND      trip.user_id = subscriber.user_id
GROUP BY subscriber.firstname,
         subscriber.lastname
ORDER BY count(trip.arrival_station_id);
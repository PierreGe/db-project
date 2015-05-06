-- Les utilisateurs, la date d'inscription, le nombre total de trajet effectues,
-- la distance totale parcourue et la distance moyenne parcourue par trajet,
-- classes en fonction de la distance totale parcourue


-- WARNING :  distance manquante

SELECT subscriber.firstname,subscriber.lastname, subscriber.entry_date, COUNT(trip.arrival_station_id) FROM subscriber,trip WHERE trip.arrival_station_id = subscriber.user_id GROUP BY subscriber.firstname,subscriber.lastname ORDER BY COUNT(trip.arrival_station_id);

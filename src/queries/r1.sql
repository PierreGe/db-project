-- Les utilisateurs habitant Ixelles ayant utilise un Villo de la station Flagey

SELECT DISTINCT subscriber.user_id,
                subscriber.firstname,
                subscriber.lastname
FROM   subscriber,
       trip
       INNER JOIN station
               ON trip.departure_station_id = station.id
WHERE  subscriber.user_id = trip.user_id
       AND station.NAME = "FLAGEY"
       AND subscriber.address_zipcode = 1050;

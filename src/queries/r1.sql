-- Les utilisateurs habitant Ixelles ayant utilise un Villo de la station Flagey

SELECT subscriber.user_id,firstname,lastname FROM subscriber,trip
    INNER JOIN station ON trip.departure_station_id = station.id
    WHERE subscriber.user_id = trip.user_id AND 
          station.name="FLAGEY" AND 
          subscriber.address LIKE '%Ixelles'
    GROUP BY subscriber.user_id;

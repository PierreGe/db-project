-- Les utilisateurs habitant Ixelles ayant utilisé un Villo de la station Flagey

SELECT * FROM subscriber,trip 
    WHERE subscriber.user_id = trip.user_id AND 
          trip.departure_station_id=14 AND 
          subscriber.address LIKE '%Ixelles';

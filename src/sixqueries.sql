


-- Les utilisateurs habitant Ixelles ayant utilisé un Villo de la station Flagey

SELECT * FROM subscriber,trip WHERE subscriber.user_id = trip.user_id AND trip.departure_station_id=14 AND subscriber.address LIKE '%Ixelles';

-- Les utilisateurs ayant utilisé Villo au moins 2 fois

SELECT id from user,trip WHERE user.id = trip.user_id GROUP BY user.id HAVING count(trip.user_id)>1;

-- Les paires d'utilisateurs ayant fait un trajet identique

-- Incomplète ? pas testé

SELECT * FROM trip trip1 WHERE EXISTS (SELECT * FROM trip trip2 WHERE trip1.user_id != trip2.user_id and trip1.arrival_station_id NOT NULL AND trip1.departure_station_id = trip2.departure_station_id AND trip1.arrival_station_id = trip2.arrival_station_id);

-- Les vélos ayant deux trajets consécutifs disjoints (station de retour du premier trajet différente de la station de départ du suivant)}

-- Les utilisateurs, la date d'inscription, le nombre total de trajet effectués, la distance totale parcourue et la distance moyenne parcourue par trajet, classés en fonction de la distance totale parcourue}

-- Les stations avec le nombre total de vélos déposés dans cette station (un même vélo peut-être comptabilisé plusieurs fois) et le nombre d'utilisateurs différents ayant utilisé la station et ce pour toutes les stations ayant été utilisées au moins 10 fois.}
-- Les utilisateurs ayant utilisé Villo au moins 2 fois

SELECT id from user,trip 
    WHERE user.id = trip.user_id 
    GROUP BY user.id 
    HAVING count(trip.user_id)>1;

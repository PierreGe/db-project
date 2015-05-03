-- Les utilisateurs ayant utilise Villo au moins 2 fois

SELECT id from user,trip 
    WHERE user.id = trip.user_id  AND
          user.expire_date IS NOT NULL
    GROUP BY user.id 
    HAVING count(trip.user_id)>1;

-- Les utilisateurs ayant utilise Villo au moins 2 fois

SELECT user_id,tripcount FROM (
    SELECT user_id,COUNT(bike_id) AS tripcount FROM trip GROUP BY bike_id)
WHERE tripcount>=2;
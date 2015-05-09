-- Les utilisateurs ayant utilise Villo au moins 2 fois

SELECT user_id FROM (
    SELECT user_id,COUNT(bike_id) AS tripcount FROM trip GROUP BY user_id)
INNER JOIN user ON user_id=user.id
WHERE tripcount>=2 AND user.expire_date NOT NULL;
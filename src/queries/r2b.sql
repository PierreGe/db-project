--  Faster proposition for R2, but used aggregate function
SELECT     user_id
FROM       (
                    SELECT   user_id,
                             Count(bike_id) AS tripcount
                    FROM     trip
                    GROUP BY user_id)
INNER JOIN USER
ON         user_id=USER.id
WHERE      tripcount>=2
AND        USER.expire_date NOT null;
-- Les utilisateurs ayant utilise Villo au moins 2 fois

SELECT DISTINCT trip1.user_id
FROM   trip trip1,
       trip trip2
WHERE  trip1.user_id = trip2.user_id
       AND trip1.departure_date != trip2.departure_date;

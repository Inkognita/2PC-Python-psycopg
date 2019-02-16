DROP DATABASE IF EXISTS db1;
DROP DATABASE IF EXISTS db2;
DROP DATABASE IF EXISTS db3;

DROP USER IF EXISTS postgres_user;
CREATE USER postgres_user WITH PASSWORD 'password';

CREATE DATABASE db1 OWNER postgres_user;
\c db1;
CREATE TABLE fly_booking
(
  id          serial PRIMARY KEY,
  client_name VARCHAR(150) NOT NULL,
  fly_number     VARCHAR(20),
  from_loc VARCHAR(5),
  to_loc VARCHAR(5),
  date timestamp
);

CREATE DATABASE db2 OWNER postgres_user;
\c db2;
CREATE TABLE hotel_booking
(
  id          serial PRIMARY KEY,
  client_name VARCHAR(150) NOT NULL,
  hotel_name     VARCHAR(20),
  arrival timestamp,
  departure timestamp
);


CREATE DATABASE db3 OWNER postgres_user;
\c db3;
CREATE TABLE account
(
  id          serial PRIMARY KEY,
  client_name VARCHAR(150) NOT NULL,
  amount     BIGINT
    CONSTRAINT positive_ammount CHECK (amount >= 0)
);
GRANT ALL PRIVILEGES ON TABLE account TO postgres_user;

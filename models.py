class Model:
    @classmethod
    def count(cls):
        return """SELECT COUNT(*) FROM {}""".format(cls.__tablename__), ()

    @classmethod
    def delete_all(cls):
        return """DELETE FROM {}""".format(cls.__tablename__), ()


class FlyBooking(Model):
    __tablename__ = "fly_booking"

    def __init__(self, id_, client_name, fly_number, from_loc, to_loc, date):
        self.id = id_
        self.client_name = client_name
        self.fly_number = fly_number
        self.from_loc = from_loc
        self.to_loc = to_loc
        self.date = date

    def update_or_create(self):
        return """INSERT INTO {} (
        id, client_name, fly_number, from_loc, to_loc, date)
         VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (id)
          DO UPDATE 
                SET client_name = EXCLUDED.client_name,
                    fly_number = EXCLUDED.fly_number,
                    from_loc = EXCLUDED.from_loc,
                    to_loc = EXCLUDED.to_loc,
                    date = EXCLUDED.date""".format(self.__tablename__), \
               [self.id,
                self.client_name, self.fly_number,
                self.from_loc, self.to_loc, self.date]


class HotelBooking(Model):
    __tablename__ = "hotel_booking"

    def __init__(self, id_, client_name, hotel_name, arrival, departure):
        self.id = id_
        self.client_name = client_name
        self.hotel_name = hotel_name
        self.arrival = arrival
        self.departure = departure

    def update_or_create(self):
        return """INSERT INTO {} (
        id, client_name, hotel_name, arrival, departure)
         VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id)
         DO UPDATE 
         SET client_name = EXCLUDED.client_name,
             hotel_name = EXCLUDED.hotel_name,
             arrival = EXCLUDED.arrival,
             departure = EXCLUDED.departure""".format(self.__tablename__), \
               [self.id, self.client_name, self.hotel_name,
                self.arrival, self.departure]


class Account(Model):
    __tablename__ = "account"

    def __init__(self, id_, client_name, amount):
        self.id = id_
        self.client_name = client_name
        self.amount = amount

    def update_or_create(self):
        return """INSERT INTO {} (id, client_name, amount) VALUES (%s, %s, %s)
        ON CONFLICT (id) DO UPDATE 
        SET client_name = EXCLUDED.client_name,
            amount = EXCLUDED.amount""".format(self.__tablename__), \
               [self.id, self.client_name, self.amount]

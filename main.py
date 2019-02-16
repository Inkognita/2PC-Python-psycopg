import psycopg2
import time


class FlyBooking:
    def __init__(self, client_name, fly_number, from_loc, to_loc, date):
        self.id = None
        self.client_name = client_name
        self.fly_number = fly_number
        self.from_loc = from_loc
        self.to_loc = to_loc
        self.date = date

    def create(self):
        return """INSERT INTO fly_booking (
        id, client_name, fly_number, from_loc, to_loc, date)
         VALUES (%s, %s, %s, %s, %s, %s)""", \
               (self.id, self.client_name, self.fly_number,
                self.from_loc, self.to_loc, self.date)

class HotelBooking:
    def __init__(self, client_name, hotel_name, arrival, departure):
        self.id = None
        self.client_name = client_name
        self.hotel_name = hotel_name
        self.arrival = arrival
        self.departure = departure

    def create(self):
        return """INSERT INTO hotel_booking (
        id, client_name, hotel_name, arrival, departure)
         VALUES (%s, %s, %s, %s, %s)""", \
               (self.id, self.client_name, self.hotel_name,
                self.arrival, self.departure)

class Account:
    def __init__(self, id_, client_name, amount):
        self.id = id_
        self.client_name = client_name
        self.amount = amount

    def create(self):
        return """INSERT INTO account (id, client_name, amount) VALUES (%s, %s, %s)""", \
               (self.id, self.client_name, self.amount)

    def update(self):
        return """UPDATE account SET client_name = %s, amount = %s where id = %s""", \
               (self.client_name, self.amount, self.id)


try:
    connection = {"db1": psycopg2.connect(user="postgres_user",
                                          password="password",
                                          host="127.0.0.1",
                                          port="5432",
                                          database="db1"),
                  "db2": psycopg2.connect(user="postgres_user",
                                          password="password",
                                          host="127.0.0.1",
                                          port="5432",
                                          database="db2"),
                  "db3": psycopg2.connect(user="postgres_user",
                                          password="password",
                                          host="127.0.0.1",
                                          port="5432",
                                          database="db3")}
    cursor = {k: v.cursor() for k, v in connection.items()}


    ammount_to_pay = 600
    acc = Account(id_=3, client_name="Bad man", amount=500)
    acc.amount -= ammount_to_pay
    fly = FlyBooking(client_name=acc.client_name, fly_number="FLY123", from_loc="LCA", to_loc="UKR", date=time.time())

    cursor["db3"].execute(*acc.update())
    cursor["db1"].execute(*fly.create())

    connection["db1"].commit()
    connection["db3"].commit()
except psycopg2.DatabaseError as error :
    print ("Error in transction Reverting all other operations of a transction ", error)
    connection["db3"].rollback()
    connection["db1"].rollback()
    connection["db2"].rollback()
finally:
    for name, con in connection.items():
        if con:
            cursor[name].close()
            con.close()

import psycopg2
import datetime


def prepare(trans, trans_name):
    return """BEGIN; {}; PREPARE TRANSACTION %s;""".format(trans[0]), \
           trans[1] + [trans_name]


def rollback(trans_name):
    return """ROLLBACK PREPARED %s;""", (trans_name,)


def commit(trans_name):
    return """COMMIT PREPARED %s;""", (trans_name,)


class FlyBooking:
    def __init__(self, id_, client_name, fly_number, from_loc, to_loc, date):
        self.id = id_
        self.client_name = client_name
        self.fly_number = fly_number
        self.from_loc = from_loc
        self.to_loc = to_loc
        self.date = date

    def create(self):
        return """INSERT INTO fly_booking (
        id, client_name, fly_number, from_loc, to_loc, date)
         VALUES (%s, %s, %s, %s, %s, %s)""", \
               [self.id, self.client_name, self.fly_number,
                self.from_loc, self.to_loc, self.date]

    @classmethod
    def count(cls):
        return """SELECT COUNT(*) FROM fly_booking"""


class HotelBooking:
    def __init__(self, id_, client_name, hotel_name, arrival, departure):
        self.id = id_
        self.client_name = client_name
        self.hotel_name = hotel_name
        self.arrival = arrival
        self.departure = departure

    def create(self):
        return """INSERT INTO hotel_booking (
        id, client_name, hotel_name, arrival, departure)
         VALUES (%s, %s, %s, %s, %s)""", \
               [self.id, self.client_name, self.hotel_name,
                self.arrival, self.departure]


class Account:
    def __init__(self, id_, client_name, amount):
        self.id = id_
        self.client_name = client_name
        self.amount = amount

    def create(self):
        return """INSERT INTO account (id, client_name, amount) VALUES (%s, %s, %s)""", \
               [self.id, self.client_name, self.amount]

    def update(self):
        return """UPDATE account SET client_name = %s, amount = %s where id = %s""", \
               [self.client_name, self.amount, self.id]

    def exists(self):
        return """SELECT COUNT(*) from account where id = %s""", \
               [self.id, ]


if __name__ == "__main__":
    try:
        params = dict(user="postgres_user",
                      password="password",
                      host="127.0.0.1",
                      port="5432")
        connection = {"db1": psycopg2.connect(database="db1", **params),
                      "db2": psycopg2.connect(database="db2", **params),
                      "db3": psycopg2.connect(database="db3", **params)}
        cursor = {k: v.cursor() for k, v in connection.items()}

        # Preparing workground

        # Deleting all flights
        cursor["db1"].execute("""DELETE FROM fly_booking""")
        connection["db1"].commit()

        # Creating account of a bad man
        acc = Account(id_=3, client_name="Bad man", amount=500)
        cursor["db3"].execute(*acc.exists())
        if cursor["db3"].fetchone()[0] == 0:
            cursor["db3"].execute(*acc.create())
        else:
            cursor["db3"].execute(*acc.update())
        connection["db3"].commit()


        # Amount to pay
        fee = 501

        # Creating the flight
        fly = FlyBooking(id_=1, client_name=acc.client_name,
                         fly_number="FLY123", from_loc="LCA",
                         to_loc="UKR", date=datetime.datetime.now())

        # Changing the balance locally
        acc.amount -= fee

        # Executing the queries
        cursor["db1"].execute(*fly.create())
        cursor["db3"].execute(*acc.update())

        # Doing the commit
        connection["db1"].commit()
        connection["db3"].commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print("Error in transction Reverting all other operations of a transction ", error)
        for con in connection.values():
            con.rollback()
    finally:
        for name, con in connection.items():
            if con:
                cursor[name].close()
                con.close()

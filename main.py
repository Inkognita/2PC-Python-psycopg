import psycopg2
import datetime
from models import Account, HotelBooking, FlyBooking


def prepare(trans, trans_name):
    return """BEGIN; {}; PREPARE TRANSACTION %s;""".format(trans[0]), \
           trans[1] + [trans_name]


def rollback(trans_name):
    return """ROLLBACK PREPARED %s;""", (trans_name,)


def commit(trans_name):
    return """COMMIT PREPARED %s;""", (trans_name,)


if __name__ == "__main__":
    params = dict(user="postgres_user",
                  password="password",
                  host="127.0.0.1",
                  port="5432")
    connection = {"db1": psycopg2.connect(database="db1", **params),
                  "db2": psycopg2.connect(database="db2", **params),
                  "db3": psycopg2.connect(database="db3", **params)}
    cursor = {k: v.cursor() for k, v in connection.items()}
    try:
        # Preparing playground

        # Deleting all previous flights
        cursor["db1"].execute(*FlyBooking.delete_all())
        connection["db1"].commit()

        # Creating account of a bad man
        acc = Account(id_=3, client_name="Bad man", amount=500)
        cursor["db3"].execute(*acc.update_or_create())
        connection["db3"].commit()

        # Amount to pay
        fee = 501

        # Creating the flight
        fly = FlyBooking(id_=1, client_name=acc.client_name,
                         fly_number="FLY123", from_loc="LCA",
                         to_loc="UKR", date=datetime.datetime.now())

        # Changing the balance locally
        acc.amount -= fee

        # creating IDENTIFIERS for PREPARED TRANSACTIONS
        xid_fly = connection["db1"].xid(42, 'foobar1', 'connection db1')
        xid_acc = connection["db3"].xid(42, 'foobar3', 'connection db3')

        # Doing PREPARE TRANSACTION for flight
        cursor["db1"].execute(*prepare(fly.update_or_create(), str(xid_fly)))
        connection["db1"].commit()
        # Doing PREPARE TRANSACTION for account fees
        cursor["db3"].execute(*prepare(acc.update_or_create(), str(xid_acc)))
        connection["db3"].commit()

        # If prepare was successful make COMMIT PREPARED
        connection["db3"].tpc_commit(xid_acc)
        connection["db1"].tpc_commit(xid_fly)
    except psycopg2.DatabaseError as error:
        print(error)
        try: connection["db1"].tpc_rollback(xid_fly)
        except: pass
        try: connection["db3"].tpc_rollback(xid_acc)
        except: pass
        for con in connection.values():
            con.rollback()
    finally:
        for name, con in connection.items():
            if con:
                cursor[name].close()
                con.close()

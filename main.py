import psycopg2
import datetime
from models import Account, HotelBooking, FlyBooking


if __name__ == "__main__":
    params = dict(user="postgres_user",
                  password="password",
                  host="127.0.0.1",
                  port="5432")
    con = {"db1": psycopg2.connect(database="db1", **params),
                  "db2": psycopg2.connect(database="db2", **params),
                  "db3": psycopg2.connect(database="db3", **params)}
    for c in con.values():
        c.autocommit = False
    cur = {k: v.cursor() for k, v in con.items()}
    try:
        # Preparing playground

        # Deleting all previous flights
        cur["db1"].execute(*FlyBooking.delete_all())
        con["db1"].commit()

        # Creating account of a bad man
        acc = Account(id_=3, client_name="Bad man", amount=500)
        cur["db3"].execute(*acc.update_or_create())
        con["db3"].commit()

        # Amount to pay (Bigger than user has)
        fee = 501

        # Creating the flight
        fly = FlyBooking(id_=1, client_name=acc.client_name,
                         fly_number="FLY123", from_loc="LCA",
                         to_loc="UKR", date=datetime.datetime.now())

        # Changing the balance locally
        acc.amount -= fee

        # creating IDENTIFIERS for PREPARED TRANSACTIONS
        xid_fly = con["db1"].xid(42, 'foobar1', 'connection db1')
        xid_acc = con["db3"].xid(42, 'foobar3', 'connection db3')

        # BEGIN;
        con["db1"].tpc_begin(xid_fly)
        con["db3"].tpc_begin(xid_acc)

        cur["db1"].execute(*fly.update_or_create())
        con["db1"].tpc_prepare()

        cur["db3"].execute(*acc.update_or_create())
        con["db3"].tpc_prepare()

        # If PREPARE was successful make COMMIT PREPARED
        con["db3"].tpc_commit()
        con["db1"].tpc_commit()
        print("Done")
    except psycopg2.DatabaseError as error:
        print("@Error:", error)
        con["db1"].tpc_rollback()
        con["db3"].tpc_rollback()
    finally:
        for name, c in con.items():
            if c:
                cur[name].close()
                c.close()

import sqlite3
import flask

class db:
    @staticmethod
    def get():
        db = getattr(flask.g, '_database', None)
        if db is None:
            db = flask.g._database = sqlite3.connect("data.db")
        return db

    @staticmethod
    def close():
        db = getattr(flask.g, '_database', None)
        if db is not None:
            db.close()

    @staticmethod
    def exec_query(q):
        cursor = db.get().cursor()
        cursor.execute(q)
        return cursor

    @staticmethod
    def commit():
        db.get().commit()

    @staticmethod
    def next_id(column, table):
        q = "SELECT {0} FROM {1} ORDER BY {0} DESC".format(column, table)
        r = db.exec_query(q).fetchone()
        return int(r[0])+1
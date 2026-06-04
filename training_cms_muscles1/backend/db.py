import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g
from backend.config import Config

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(Config.DATABASE_URL, cursor_factory=RealDictCursor)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_one(sql, params=None):
    cur = get_db().cursor()
    cur.execute(sql, params)
    return cur.fetchone()

def query_all(sql, params=None):
    cur = get_db().cursor()
    cur.execute(sql, params)
    return cur.fetchall()

def execute(sql, params=None):
    cur = get_db().cursor()
    cur.execute(sql, params)
    get_db().commit()
    return cur.lastrowid

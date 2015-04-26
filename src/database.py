# -*- coding: utf-8 -*-

from config import DATABASE
from flask import g
import sqlite3

def connect():
    return sqlite3.connect(DATABASE)

def query(query, args=(), one=False):
    cur = getDB().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def getDB():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = connect()
    return db
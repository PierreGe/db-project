from flask import g
from models import Database

def get_db():
    if not hasattr(g, '_db'):
        g._db = Database()
    return g._db

# -*- coding: utf-8 -*-

from flask import session
from apputils import get_db

def connect_user(user):
    session['user_id'] = user.id

def current_user():
    if 'user_id' in session:
        return get_db().User.get(session['user_id'])
    return None

def disconnect_user():
    """ remove the username from the session if it's there """
    session.pop('user_id', None)

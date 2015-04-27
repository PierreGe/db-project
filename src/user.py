# -*- coding: utf-8 -*-

from flask import session


def checkLoginPassword(login, password):
    if login == "admin" and password =="admin":
        return True
    return False

def connectUser(usern):
    session['username'] = usern

def disconnectUser():
    """ remove the username from the session if it's there """
    session.pop('username', None)

def isConnected():
    return 'username' in session

def getUserName():
    return session['username']

DATABASE = "test.sqlite"
PASSWD_SALT = "3sTeB4nD4n53lA54154"
DEBUG = True
WEB_ADDRESS = '127.0.0.1'
WEB_PORT = 5000

# Site-specific config
try:
    from local_config import *
except:
    pass

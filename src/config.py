DATABASE = "test.sqlite"
PASSWD_SALT = "3sTeB4nD4n53lA54154"

# Site-specific config
try:
    from local_config import *
except:
    pass

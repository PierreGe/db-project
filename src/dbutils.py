import hashlib
from datetime import datetime
from config import PASSWD_SALT

def hash_password(passwd):
    cipher = hashlib.sha256()
    cipher.update(PASSWD_SALT)
    cipher.update(passwd)
    return ''.join(map(lambda x: "%02x" % ord(x), cipher.digest()))

# Sanitize an argument for insertion
def sanitize(arg):
    if isinstance(arg, str) or isinstance(arg, unicode):
        return arg.replace('"', '\\"')
    elif isinstance(arg, datetime):
        return arg.strftime("%Y-%m-%dT%H:%M:%S")
    else:
        return str(arg)


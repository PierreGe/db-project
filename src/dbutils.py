import hashlib
from config import PASSWD_SALT

def hash_password(passwd):
    cipher = hashlib.sha256()
    cipher.update(PASSWD_SALT)
    cipher.update(passwd)
    return ''.join(map(lambda x: "%02x" % ord(x), cipher.digest()))

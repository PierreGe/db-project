DATABASE = "test.sqlite"

# Site-specific config
try:
    from local_config import *
except:
    pass

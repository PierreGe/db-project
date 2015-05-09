# db-project

## Install

### Install sys packages

    $ apt-get install sqlite3 libsqlite3-dev python-virtualenv

### Install Python packages

    $ virtualenv ve
    $ source ve/bin/activate
    $ pip install -r requirements.txt
    
### Create sqlite3 geodistance extension

    $ cd src/
    $ make

### Run tests

    $ py.test
    $ sqlite3 test.sqlite -init .sqliterc < queries/r5.sql
    
## Run webapp

    $ python main.py

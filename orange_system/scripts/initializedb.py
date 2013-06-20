import os
import sys
import transaction
from csv import reader

from sqlalchemy import engine_from_config
from sqlalchemy.exc import DBAPIError

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from ..models import *


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    
    #Initializing classes from models.py
    
    # When we want to add an object to the database,
    # we have to initialize it with the properties defined in models.py
    # Ex: If we want to insert a customer and our corresponding class
    # is Customers, we would instantiate this with
    # somevariablename = Customer(properties)
    # where properties are the parameters of __init__ in the class
        

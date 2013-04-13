import os
import sys
import transaction

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
    with transaction.manager:
        wisconsin = States('WI', 'Wisconsin')
        finished = Progress( 'Finished')
        inProgress = Progress( 'In Progress')
        hdd300gb = Parts( 'Western Digital 300GB', '$3.50')
        hddReplace = Services('Replace Hard Drive', '$3.50')
        workEmail = EmailType('Work Email')
        publicEmail = EmailType('Public E-mail')
        homePhone = PhoneType('ET Phone Home')
        bananaPhone = PhoneType('Ring ring ring ring, banana phone!')
        workPhone = PhoneType('Work Phone')
        testCust1 = Customers( 'test1', 'test', '123 test', 'test', 'WI', '54669')
        testCust2 = Customers( 'test2', 'test', '123 test', 'test', 'WI', '54601')
        testOrder = Orders( '1', 'GBook Lamer', 'Some notes', '$3.50', '2013.04.08', '2013.04.08', 'Finished')
        email1 = Email( '1', 'test1@test.com', 'Work Email')
        email2 = Email( '1', 'test1@test.gov', 'Public Email')
        email3 = Email('2', 'test2@test.com', 'Public Email')
        email4 = Email( '2', 'test2@test.gov', 'Work Email')
        phone1 = Phone('1', '6083866066', 'Work Phone')
        phone2 = Phone('1', '6087680022', 'Home Phone')
        phone3 = Phone('2', '3866622443', 'Home Phone')
        phone4 = Phone('2', '1234567890', 'Ring ring ring ring, banana phone!')
        partToOrder = PartsByOrder('Western Digital 300GB', '1')
        serviceToOrder = ServicesByOrder('Replace Hard Drive', '1')
   
    # Next, we want to query the DB Session to insert these objects.
    # The format for this is:
    # DBSession.add(Instance)
        try:
	    DBSession.add(wisconsin)
	    DBSession.add(finished)
	    DBSession.add(inProgress)
	    DBSession.add(hdd300gb)
            DBSession.add(hddReplace)
            DBSession.add(workEmail)
            DBSession.add(publicEmail)
            DBSession.add(homePhone)
            DBSession.add(bananaPhone)
            DBSession.add(workPhone)
            DBSession.add(testCust1)
            DBSession.add(testCust2)
            DBSession.add(testOrder)
            DBSession.add(email1)
            DBSession.add(email2)
            DBSession.add(email3)
            DBSession.add(email4)
            DBSession.add(phone1)
            DBSession.add(phone2)
            DBSession.add(phone3)
            DBSession.add(phone4)
            DBSession.add(partToOrder)
            DBSession.add(serviceToOrder)
    # We obviously wouldn't normally run so many requests to the
    # database all at once, but this is just test data for the
    # initialization script, and won't be called at runtime.
    # Next, we need to catch any DB errors.
        except DBAPIError:
            print "Something bad happened :("
    print "Yay it worked!"
        

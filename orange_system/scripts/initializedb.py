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
        finished = Progress('F', 'Finished')
        inProgress = Progress('IP', 'In Progress')
        hdd300gb = Parts('HDD300GB', 'Western Digital 300GB', '300GB SATA Hard Drive', '$3.50')
        hddReplace = Services('hddReplace', 'Replaced Hard Drive', 'Replace internal hard drive', '$3.50')
        workEmail = EmailType('workEmail', 'Work E-Mail Address')
        publicEmail = EmailType('publicEmail', 'Public E-mail Address')
        homePhone = PhoneType('homePhone', 'ET Phone Home')
        bananaPhone = PhoneType('banana', 'Ring ring ring ring, banana phone!')
        workPhone = PhoneType('workPhone', 'Work Phone Number')
        testCust1 = Customers('testCust1', 'test1', 'test', '123 test', 'test', 'WI', '54669')
        testCust2 = Customers('testCust2', 'test2', 'test', '123 test', 'test', 'WI', '54601')
        testOrder = Orders('order1', 'testCust1', 'GBook Lamer', 'Some notes', '$3.50', '2013.04.08', '2013.04.08', 'F')
        email1 = Email('eml1', 'testCust1', 'test1@test.com', 'workEmail')
        email2 = Email('eml2', 'testCust1', 'test1@test.gov', 'publicEmail')
        email3 = Email('eml3', 'testCust2', 'test2@test.com', 'publicEmail')
        email4 = Email('eml4', 'testCust2', 'test2@test.gov', 'workEmail')
        phone1 = Phone('phon1', 'testCust1', '6083866066', 'workPhone')
        phone2 = Phone('phon2', 'testCust1', '6087680022', 'homePhone')
        phone3 = Phone('phon3', 'testCust2', '3866622443', 'homePhone')
        phone4 = Phone('phon4', 'testCust2', '1234567890', 'banana')
        partToOrder = PartsByOrder('1', 'HDD300GB', 'testOrder')
        serviceToOrder = ServicesByOrder('1', 'hddReplace', 'testOrder')
   
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
        

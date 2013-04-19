from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    String,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from zope.sqlalchemy import ZopeTransactionExtension

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

"""
This section is where the database tables are defined.  I'm not going to explain the syntax in detail, as there is plenty
of documentation on SqlAlchemy right on the website.  The basic idea is that each table in here is its own object,
consisting of each of its fields as an element.  In our case, when you run ../../venv/bin/initialize_capstone_project_db, it will
process this file and convert each class into a create table sql query, saving the results as a sqlite file in your
project root.  To add a new table, simply add in a class detailing the specs of the table and run initialize_{project name}_db
in the bin folder of your venv.  This is not the only way of doing this, as you might read in the docs.  You can also have each table
in its own script if you like.  However, our database is small so we'll just throw all the tables in here.
"""



class States(Base):
    __tablename__ = 'tblStates'
    stateCode = Column(String(2), primary_key=True)
    stateName = Column(String(25), nullable=False)
    def __init__(self, stateCode, stateName):
        self.stateCode = stateCode
        self.stateName = stateName
  
class Progress(Base):
    __tablename__ = 'tblProgress'
    __tableargs__ = ({
    'sqlite_autoincrement': True})
    progressID = Column(Integer, primary_key=True)
    progressDescription = Column(String(25), unique=True)

    def __init__(self, progressDescription):
        self.progressDescription = progressDescription  

class Parts(Base):
    __tablename__ = 'tblParts'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    partID   = Column(Integer, primary_key=True)
    partName = Column(String(20), unique=True)
    partCost = Column(String(5))

    def __init__(self, partName, partCost):
	self.partName = partName
	self.partCost = partCost

class Services(Base):
    __tablename__ = 'tblServices'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    serviceID   = Column(Integer, primary_key=True)
    serviceName = Column(String(20), unique=True)
    serviceCost = Column(String(5))

    def __init__(self, serviceName, serviceCost):
	self.serviceName = serviceName
	self.serviceCost = serviceCost
	
class EmailType(Base):
    __tablename__ = 'tblEmailType'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    emailID   = Column(Integer, primary_key=True)
    emailType = Column(String(20), unique=True)

    def __init__(self, emailType):
	self.emailType = emailType

class PhoneType(Base):
    __tablename__= 'tblPhoneType'
    __tableargs__= ({
    'sqlite_autoincrement': True})
    phoneTypeID = Column(Integer, primary_key=True)
    phoneType = Column(String(20), unique=True)

    def __init__(self, phoneType):
    	self.phoneType = phoneType

class Customers(Base):
    __tablename__ = 'tblCustomers'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    customerID    = Column(Integer, primary_key=True, unique = True)
    firstName = Column(String(15), unique=False)
    lastName  = Column(String(25), unique=False)
    address   = Column(String(50))
    city      = Column(String(15), unique=False)
    stateCode = Column(String(2), ForeignKey(States.stateCode), unique=False)
    zipCode   = Column(String(9), unique=False)
    def __init__(self, firstName, lastName, address, city, stateCode, zipCode):
        self.firstName = firstName
	self.lastName  = lastName
        self.address   = address
	self.city      = city
	self.stateCode = stateCode
	self.zipCode   = zipCode

class Orders(Base):
    __tablename__ = 'tblOrders'
    __tableargs__ = ({
    'sqlite_autoincrement': True})
    orderID = Column(Integer, primary_key=True, unique=True)
    custID  = Column(Integer(10), ForeignKey(Customers.customerID))
    modelName = Column(String(25))
    orderNotes = Column(String(200))
    orderCost = Column(String(10))
    entryDate = Column(String(10))
    completionDate = Column(String(10))
    progressDescription = Column(String(10), ForeignKey(Progress.progressDescription))

    def __init__(self, custID, modelName, orderNotes, orderCost, entryDate, completionDate, progressDescription):
	self.custID = custID
	self.modelName = modelName
	self.orderNotes = orderNotes
	self.orderCost = orderCost
	self.entryDate = entryDate
	self.completionDate = completionDate
	self.progressDescription = progressDescription




class Email(Base):
    __tablename__ = 'tblEmail'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    emailID = Column(Integer, primary_key=True)
    custID = Column(String(10), ForeignKey(Customers.customerID))
    emailAddress = Column(String(254), unique=True)
    emailType = Column(String(20), ForeignKey(EmailType.emailType))

    def __init__(self, custID, emailAddress, emailType):
        self.custID = custID
	self.emailAddress = emailAddress
	self.emailType = emailType

class Phone(Base):
    __tablename__ = 'tblPhone'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    phoneID = Column(Integer, primary_key=True)
    custID = Column(String(10), ForeignKey(Customers.customerID))
    phoneNumber = Column(String(10))
    phoneType = Column(String(10), ForeignKey(PhoneType.phoneType))

    def __init__(self, custID, phoneNumber, phoneType):
	self.custID = custID
	self.phoneNumber = phoneNumber
	self.phoneType = phoneType





class PartsByOrder(Base):
    __tablename__ = 'tblPartsByOrder'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    partID = Column(Integer, primary_key=True)
    partName = Column(String(10), ForeignKey(Parts.partName))
    orderID = Column(String(10), ForeignKey(Orders.orderID))

    def __init__(self,  partName, orderID):
	self.partName = partName
	self.orderID = orderID

class ServicesByOrder(Base):
    __tablename__ = 'tblServicesByOrder'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    serviceID = Column(Integer, primary_key=True)
    serviceName = Column(String(10), ForeignKey(Services.serviceName))
    orderID = Column(String(10), ForeignKey(Orders.orderID))

    def __init__(self, serviceName, orderID):
        
	self.serviceName = serviceName
	self.orderID = orderID


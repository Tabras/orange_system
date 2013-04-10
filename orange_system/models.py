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
  
class Progress(Base):
    __tablename__ = 'tblProgress'
    progressID = Column(String(10), primary_key=True)
    progressDescription = Column(String(200))

    def __init__(self, progressID, progressDescription):
        self.progressID = progressID
        self.progressDescription = progressDescription  

class Parts(Base):
    __tablename__ = 'tblParts'
    partID = Column(String(10), primary_key=True)
    partName = Column(String(15))
    partDescription = Column(String(200))
    partCost = Column(String(5))

    def __init__(self, partID, partName, partDescription, partCost):
	self.partID = partID
	self.partName = partName
	self.partDescription = partDescription
	self.partCost = partCost

class Services(Base):
    __tablename__ = 'tblServices'
    serviceID = Column(String(10), primary_key=True)
    serviceName = Column(String(15))
    serviceDescription = Column(String(200))
    serviceCost = Column(String(5))

    def __init__(self, serviceID, serviceName, serviceDescription, serviceCost):
	self.serviceID = serviceID
	self.serviceName = serviceName
	self.serviceDescription = serviceDescription
	self.serviceCost = serviceCost
	
class EmailType(Base):
    __tablename__ = 'tblEmailType'
    emailType = Column(String(10), primary_key=True)
    emailTypeDescription = Column(String(15))

    def __init__(self, emailType, emailTypeDescription):
	self.emailType = emailType
	self.emailTypeDescription = emailTypeDescription

class PhoneType(Base):
    __tablename__= 'tblPhoneType'
    phoneType = Column(String(10), primary_key=True)
    phoneTypeDescription = Column(String(15))

    def __init__(self, phoneType, phoneTypeDescription):
    	self.phoneType = phoneType
	self.phoneTypeDescription = phoneTypeDescription

class Customers(Base):
    __tablename__ = 'tblCustomers'
    custID    = Column(String(10), primary_key=True, unique = True)
    firstName = Column(String(15), unique=False)
    lastName  = Column(String(25), unique=False)
    address   = Column(String(50))
    city      = Column(String(15), unique=False)
    stateCode = Column(String(2), ForeignKey(States.stateCode), unique=False)
    zipCode   = Column(String(9), unique=False)

    def __init__(self, custID, firstName, lastName, city, stateCode, zipCode):
        self.custID = custID
        self.firstName = firstName
	self.lastName  = lastName
	self.city      = city
	self.stateCode = stateCode
	self.zipCode   = zipCode

class Orders(Base):
    __tablename__ = 'tblOrders'
    orderID = Column(String(10), primary_key=True, unique=True)
    custID  = Column(String(10), ForeignKey(Customers.custID))
    modelName = Column(String(25))
    orderNotes = Column(String(200))
    orderCost = Column(String(10))
    entryDate = Column(String(10))
    completionDate = Column(String(10))
    progressID = Column(String(10), ForeignKey(Progress.progressID))

    def __init__(self, orderID, custID, modelName, orderNotes, orderCost, entryDate, completionDate, progressID):
        self.orderID = orderID
	self.custID = custID
	self.modelName = modelName
	self.orderNotes = orderNotes
	self.orderCost = orderCost
	self.entryDate = entryDate
	self.completionDate = completionDate
	self.progressID = progressID




class Email(Base):
    __tablename__ = 'tblEmail'
    emailID = Column(String(5), primary_key=True)
    custID = Column(String(10), ForeignKey(Customers.custID))
    emailAddress = Column(String(254))
    emailType = Column(String(20), ForeignKey(EmailType.emailType))

    def __init__(self, emailID, custID, emailAddress, emailType):
        self.emailID = emailID
        self.custID = custID
	self.emailAddress = emailAddress
	self.emailType = emailType

class Phone(Base):
    __tablename__ = 'tblPhone'
    phoneID = Column(String(5), primary_key=True)
    custID = Column(String(10), ForeignKey(Customers.custID))
    phoneNumber = Column(String(10))
    phoneType = Column(String(10), ForeignKey(PhoneType.phoneType))

    def __init__(self, phoneID, custID, phoneNumber, phoneType):
	self.phoneID = phoneID
	self.custID = custID
	self.phoneNumber = phoneNumber
	self.phoneType = phoneType





class PartsByOrder(Base):
    __tablename__ = 'tblPartsByOrder'
    autoID = Column(Integer(1), primary_key=True)
    partID = Column(String(10), ForeignKey(Parts.partID))
    orderID = Column(String(10), ForeignKey(Orders.orderID))

    def __init__(self, autoID, partID, orderID):
	self.autoID = autoID
	self.partID = partID
	self.orderID = orderID

class ServicesByOrder(Base):
    __tablename__ = 'tblServicesByOrder'
    autoID = Column(Integer(1), primary_key=True)
    serviceID = Column(String(10), ForeignKey(Services.serviceID))
    orderID = Column(String(10), ForeignKey(Orders.orderID))

    def __init__(self, autoID, serviceID, orderID):
	self.autoID = autoID
	self.serviceID = serviceID
	self.orderID = orderID


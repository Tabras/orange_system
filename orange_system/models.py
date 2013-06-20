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
    __tablename__ = 'states'
    state_code = Column(String(2), primary_key=True)
    state_name = Column(String(25), nullable=False)
    def __init__(self, stateCode, stateName):
        self.state_code = stateCode
        self.state_name = stateName
  
class Progress(Base):
    __tablename__ = 'tblProgress'
    __tableargs__ = ({
    'sqlite_autoincrement': True})
    progressID = Column(Integer, primary_key=True)
    progressDescription = Column(String(25), unique=True)

    def __init__(self, progressDescription):
        self.progressDescription = progressDescription  

class Parts(Base):
    __tablename__ = 'items'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    id  = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    cost = Column(Integer())

    def __init__(self, partName, partCost):
		self.name = partName
		self.cost = partCost

class Services(Base):
    __tablename__ = 'services'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    id   = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True)
    cost = Column(String(5))

    def __init__(self, serviceName, serviceCost):
		self.name = serviceName
		self.cost = serviceCost
	
class EmailType(Base):
    __tablename__ = 'email_type'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    id   = Column(Integer, primary_key=True)
    email_type = Column(String(20), unique=True)

    def __init__(self, emailType):
		self.email_type = emailType

class PhoneType(Base):
    __tablename__= 'phone_type'
    __tableargs__= ({
    'sqlite_autoincrement': True})
    id = Column(Integer, primary_key=True)
    phone_type = Column(String(20), unique=True)

    def __init__(self, phoneType):
    	self.phone_type = phoneType


class Customers(Base):
    __tablename__ = 'users'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    id    = Column(Integer, primary_key=True, unique = True)
    first_name = Column(String(15), unique=False)
    middle_name = Column(String(25))
    last_name  = Column(String(25), unique=False)
    def __init__(self,first_name, middle_name, last_name):
        self.firstName = first_name
        self.middle_name = middle_name
        self.lastName  = last_name

class Addresses(Base):
    __tablename__ = 'addresses'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    id = Column(Integer(), primary_key=True, unique = True)
    user_id = Column(Integer(), ForeignKey(Customers.id))
    zip_code = Column(Integer(5))
    city = Column(String())
    state = Column(String(2), ForeignKey(States.state_code))
    street = Column(String())

    def __init__(self, user_id, zip_code, city, state, street):
        self.user_id = user_id
        self.zip_code = zip_code
        self.city = city
        self.state = state
        self.street = street


class Orders(Base):
    __tablename__ = 'receipts'
    __tableargs__ = ({
    'sqlite_autoincrement': True})
    id = Column(Integer, primary_key=True, unique=True)
    user_id  = Column(Integer(10), ForeignKey(Customers.id))
    #model_name = Column(String(25)) <-- Not present in DB.  Needs to be added as a column in the future.
    total_cost = Column(Integer())
    created_at = Column(String())
    updated_at = Column(String())
    status  = Column(String(10), ForeignKey(Progress.progressDescription))

    def __init__(self, custID, modelName, orderNotes, orderCost, entryDate, completionDate, progressDescription):
		self.custID = custID
		self.modelName = modelName
		self.orderNotes = orderNotes
		self.orderCost = orderCost
		self.entryDate = entryDate
		self.completionDate = completionDate
		self.progressDescription = progressDescription

class Email(Base):
    __tablename__ = 'emails'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey(Customers.id))
    email = Column(String(254), unique=True)
    email_type = Column(String(20), ForeignKey(EmailType.email_type))

    def __init__(self, user_id, email, email_type):
		self.user_id = user_id
		self.emailAddress = email
		self.email_type = email_type

class Phone(Base):
    __tablename__ = 'phones'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    id = Column(Integer, primary_key=True)
    user_id = Column(String(10), ForeignKey(Customers.id))
    number = Column(String(10))
    phone_type = Column(String(10), ForeignKey(PhoneType.phone_type))

    def __init__(self,user_id, number, phone_type):
		self.user_id = user_id
		self.phoneNumber = phoneNumber
		self.phone_type = phone_type

class PartsByOrder(Base):
    __tablename__ = 'itemorders'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    id = Column(Integer, primary_key=True)
    item_id = Column(String(10), ForeignKey(Parts.id))
    receipt_id = Column(String(10), ForeignKey(Orders.id))

    def __init__(self,  item_id, receipt_id):
		self.item_id = item_id
		self.receipt_id = receipt_id
               


class ServicesByOrder(Base):
    __tablename__ = 'serviceorders'
    __tableargs__ = ({
    'sqlite_autoincrement': True,})
    id = Column(Integer, primary_key=True)
    service_id = Column(String(10), ForeignKey(Services.id))
    receipt_id = Column(String(10), ForeignKey(Orders.id))

    def __init__(self, serviceID, orderID):
        
		self.service_id = serviceID
		self.receipt_id = orderID



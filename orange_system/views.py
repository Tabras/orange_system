from pyramid.response import Response
from pyramid.view import view_config
import locale
import  transaction
from sqlalchemy.exc import DBAPIError
from sqlalchemy import *

from pyramid.httpexceptions import HTTPFound
from .models import (
    DBSession,
    Customers,
    Email,
    Phone,
    Orders,
    States,
    Services,
    Parts,
    EmailType,
    PhoneType,
    Progress,
    )

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'orange_system'}

@view_config(route_name='search', renderer='templates/searchTemplate.pt')
def search_view(request):
    result = None
    if 'q' in request.GET:
        search = request.GET.get('q')
        # Monster query right here.  This one is very dependant on some
        # Sqlite syntax, so using the ORM would require us to extend it a bit.
        # For simplicity sake, let's just execute raw SQL :)
        result = DBSession.execute(\
        "SELECT c.customerID, c.firstName, c.lastName, c.address, c.city, c.stateCode,"+\
        " c.zipCode, group_concat(DISTINCT e.emailAddress) AS 'emails', "+\
        "group_concat(DISTINCT p.phoneNumber) AS 'Phone Number' "+\
        "FROM tblCustomers AS c "+\
        # We're using a left join here because we need to pull in all
        # customers regardless of whether or not they have an email or phone
        # number.
        "LEFT JOIN tblEmail AS e ON c.customerID = e.custID "+\
        "LEFT JOIN tblPhone AS p ON c.customerID = p.custID "+\
        # Here's the magic of the query.  We're doing a wildcard search on all
        # fields we want to test against the search query.  This is how only
        # relevant data is extracted.
        "WHERE c.firstName LIKE '%" + search + "%' OR "+\
        "c.lastName LIKE '%" + search + "%' OR "+\
        "c.address LIKE '%" + search + "%' OR "+\
        "c.city LIKE '%" + search + "%' OR "+\
        "c.stateCode LIKE '%" + search + "%' OR "+\
        "c.zipCode LIKE '%" + search + "%' OR "+\
        "e.emailAddress LIKE '%" + search + "%' OR "+\
        "p.phoneNumber LIKE '%" + search + "%' AND "+\
        "e.emailAddress != 'none' AND p.phoneNumber != 'none' "+\
        "GROUP BY c.customerID")
        
    return {'project': 'orange_system', 'result': result}

@view_config(route_name='customer', renderer='templates/customerTemplate.pt')
def customer_view(request):
	# We need to fetch the states to populate the selection box
    states = DBSession.query(States).all()
    # We also need to fetch phone type and email type descriptors
    emailTypes = DBSession.query(EmailType).all()
    phoneTypes = DBSession.query(PhoneType).all()
    # We also need to initialize all of our return variables
    customer = None
    newCustomer = None
    customerEmail = None
    customerPhone = None
    if 'customerID' in request.GET:
                # We're going to store this in a local variable to make our life easier when updating the customer
		# Let's find the customer associated with the ID we passed from the search page
		customer = DBSession.query(Customers).filter(Customers.customerID == request.GET['customerID']).first()
		# As well as any email addresses and phone numbers associated with them.
		customerEmail = DBSession.query(Email).filter(Email.custID == request.GET['customerID']).all()
		customerPhone = DBSession.query(Phone).filter(Phone.custID == request.GET['customerID']).all() 
    return {'project': 'orange_system', 
    'states': states,
    'customer': customer,
    'phoneTypes': phoneTypes,
    'emailTypes': emailTypes,
    'customerEmail': customerEmail,
    'customerPhone': customerPhone,}

@view_config(route_name='addEmail', request_method="POST", renderer='json')
def addEmail_view(request):
    print request.POST
    latestCustomer = DBSession.query(Customers).order_by(Customers.customerID.desc()).first()
    latestID = latestCustomer.customerID
    email = Email(latestID, request.POST['emailAddress'], request.POST['emailType'])
    DBSession.add(email)
    return {'data': 'test'}

@view_config(route_name='addCust', request_method="POST", renderer='json')
def addCust_view(request):
    cust = Customers(
    request.POST['firstName'],
    request.POST['lastName'],
    request.POST['address'],
    request.POST['city'],
    request.POST['stateCode'],
    request.POST['zipCode'])
 
    DBSession.add(cust)
    return {'data': 'test'}

@view_config(route_name='addPhone', request_method="POST", renderer='json')
def addPhone_view(request):
     latestCustomer = DBSession.query(Customers).order_by(Customers.customerID.desc()).first()
     latestID = latestCustomer.customerID
     phone = Phone(latestID, request.POST['phoneNumber'], request.POST['phoneType'])
     DBSession.add(phone)
     return {}

@view_config(route_name='addEmailExisting', request_method="POST", renderer='json')
def addEmailExisting_view(request):
     print "test"
     print request.POST
     custID = request.POST['customerID']
     email = request.POST['emailAddress']
     emailtype = request.POST['emailType']
     
     newEmail = Email(custID, email, emailtype)
     DBSession.add(newEmail)
     return {}

@view_config(route_name='addPhoneExisting', request_method="POST", renderer='json')
def addPhoneExisting_view(request):
    custID = request.POST['customerID']
    phone = request.POST['phoneNumber']
    phoneType = request.POST['phoneType']
    
    newPhone = Phone(custID, phone, phoneType)
    DBSession.add(newPhone)
    return {}
    
@view_config(route_name='updateCust', request_method="POST", renderer='json')
def updateCust_view(request):
	custID = request.POST['customerID']
	firstName = request.POST['firstName']
	lastName = request.POST['lastName']
	address = request.POST['address']
	city = request.POST['city']
	stateCode = request.POST['stateCode']
	zipCode = request.POST['zipCode']
        
        for i in range(0, int(request.POST['emailLength'])):
            print request.POST['emailInfo['+str(i)+'][name]']
            print request.POST['emailInfo['+str(i)+'][value]']
	return {}
    
@view_config(route_name='deleteCust', request_method="POST", renderer='json')
def deleteCust_view(request):
    print request.POST
    custID = request.POST['formData[0][value]']
    DBSession.query(Email).filter(Email.custID == custID).delete()
    DBSession.query(Phone).filter(Phone.custID == custID).delete()
    DBSession.query(Customers).filter(Customers.customerID == custID).delete()
    return {}
@view_config(route_name='order', renderer='templates/orderTemplate.pt')
def order_view(request):
	# here we are pulling in all the current orders for display
	orders = DBSession.query(Orders).all()
	
	# We need to fetch service, part, and progress names for the select boxes
	services = DBSession.query(Services).all()
	parts = DBSession.query(Parts).all()
	progress = DBSession.query(Progress).all()
	
	# initializing necessary values before declaring them
	order = None
	newOrder = None
	
	# looking for the order id to be passed
	if 'orderID' in request.GET:
		# here we are finding the order associated with the id that was just passed from the order page
		order = DBSession.query(Orders).filter(Orders.orderID == request.GET[orderID]).first()
	
	return {'project': 'orange_system', 
	'orders': orders, 
	'order': order, 
	'services': services, 
	'parts': parts, 
	'progress': progress,}
	
@view_config(route_name='addOrder', request_method="POST", renderer='json')
def addOrder_view(request):
    order = Orders(
    request.POST['custID'],
    request.POST['modelName'],
    request.POST['orderNotes'],
    request.POST['entryDate'],
    request.POST['progressDescription'])
 
    DBSession.add(order)
    return {'data': 'test'}
    
@view_config(route_name='service', renderer='templates/serviceTemplate.pt')
def service_view(request):
	serviceList = None
	serviceAdd = None
	name = None
	cost = None
	serviceList = DBSession.query(Services).all()
	
	if request.POST:
		if request.POST['servicename'] and request.POST['servicecost']:
			name = request.POST['servicename']
			cost = request.POST['servicecost']
			service = Services(name, cost)
			print service.serviceName
			if service:
				DBSession.add(service)
       
	return {'project': 'orange_system', 'serviceList': serviceList}
    
@view_config(route_name='part', renderer='templates/partTemplate.pt')
def part_view(request):
	partList = None
	partAdd = None
	part = None
	partList = DBSession.execute(\
	"SELECT * "+\
	"FROM tblParts")
	
	if request.POST:
		name = request.POST['partname']
		cost = request.POST['partcost']
		part = Parts(name, cost)
		if part:
		    DBSession.add(part)
		
	return {'project': 'orange_system', 'partList': partList}
    
@view_config(route_name='report', renderer='templates/reportTemplate.pt')
def report_view(request):
    return {'project': 'orange_system'}
    
@view_config(route_name='todo', renderer='templates/todoTemplate.pt')
def todo_view(request):
    # We want to pull in any orders that are not finished yet.  We need
    # group_concat again for this one so we can get a concatenated field containing
    # all parts/services to the order we use fetchall() here to bypass
    # the ORM and obtain our result as a generic list.  You'll see why down further.
    todoList = DBSession.execute(\
    "SELECT o.orderID, o.custID, o.modelName, o.orderNotes, o.orderCost, o.entryDate, "+\
    "o.progressDescription, "+\
    "group_concat(DISTINCT p.partName) AS partsOnOrder, "+\
    "group_concat(DISTINCT s.serviceName) AS servicesOnOrder "+\
    "FROM tblOrders AS o "+\
    "LEFT JOIN tblPartsByOrder AS p ON o.orderID = p.orderID "+\
    "LEFT JOIN tblServicesByOrder AS s ON o.orderID = p.orderID "+\
    "WHERE o.progressDescription != 'Finished' "+\
    "GROUP BY o.orderID").fetchall()
    # We want to filter out the high priority orders so we can push them
    # to the top and give them some nice visuals.  Sounds like a perfect
    # time for some list comprehension.
    # This first statement will iterate our todoList and add only rows that
    # contain a 'critical' tag in their progress description.
    priorityList = [row for row in todoList if 'critical' in row['progressDescription'].lower()]
    # Next, we reverse the process for non-priority orders.
    newToDoList = [row for row in todoList if 'critical' not in row['progressDescription'].lower()]
    # Fun, right? :)
    return {'project': 'orange_system', 'todoList': newToDoList, 'priorityList': priorityList}
    
conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_capstone_project_db" script
    to initialize your database tables.  Check your virtual 
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""


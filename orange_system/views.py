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
    EmailType,
    PhoneType
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
		# Let's find the customer associated with the ID we passed from the search page
		customer = DBSession.query(Customers).filter(Customers.customerID == request.GET['customerID']).first()
		# As well as any email addresses and phone numbers associated with them.
		customerEmail = DBSession.query(Email).filter(Email.custID == request.GET['customerID']).all()
		customerPhone = DBSession.query(Phone).filter(Phone.custID == request.GET['customerID']).all() 
    if request.POST:
        # Check to see if the post data is present
        if request.POST['firstname'] and request.POST['lastname'] \
        and request.POST['address'] and request.POST['city'] \
        and request.POST['state'] and request.POST['zipcode']:
        # Create an instance of Customers with the post data
            newCustomer = Customers(
            request.POST['firstname'], request.POST['lastname'],
            request.POST['address'], request.POST['city'],
            request.POST['state'], request.POST['zipcode'])
        # Instruct the server to notify us that we created the object
            if newCustomer:
                DBSession.add(newCustomer)
                firstName = request.POST['firstname']
                # Let's get the ID of our new customer
                newCust = DBSession.query(Customers).filter(Customers.firstName == firstName).first()
                newID = newCust.customerID
        # Check to see if there is email information in POST
            if request.POST['email1']:
            # Instantiate an email object with the fetched ID
                email1 = Email(newID,request.POST['email1'],
                request.POST['emailtype1'])
            # And add the new object to our database
                DBSession.add(email1)
            if request.POST['email2']:
                email2 = Email(newID,request.POST['email2'],
                request.POST['emailtype2'])
                DBSession.add(email2)
				
            if request.POST['email3']:
                email3 = Email(newID,request.POST['email3'],
                request.POST['emailtype3'])
                DBSession.add(email3)
            
        # Let's do the same thing for phone numbers.
            if request.POST['phone1']:
                phone1 = Phone(newID,request.POST['phone1'],
                request.POST['phonetype1'])
                DBSession.add(phone1)
            if request.POST['phone2']:
                phone2 = Phone(newID,request.POST['phone2'],
                request.POST['phonetype2'])
                DBSession.add(phone2)
            if request.POST['phone3']:
                phone3 = Phone(newID,request.POST['phone3'],
                request.POST['phonetype3'])
                DBSession.add(phone3)
    return {'project': 'orange_system', 
    'states': states,
    'customer': customer,
    'phoneTypes': phoneTypes,
    'emailTypes': emailTypes,
    'customerEmail': customerEmail,
    'customerPhone': customerPhone,}
    
@view_config(route_name='order', renderer='templates/orderTemplate.pt')
def order_view(request):
    orders = DBSession.query(Orders).all()
    return {'project': 'orange_system', 'orders': orders}
    
@view_config(route_name='service', renderer='templates/serviceTemplate.pt')
def service_view(request):
	serviceList = None
	serviceAdd = None
	serviceList = DBSession.execute(\
	"SELECT serviceID, serviceName, serviceCost "+\
	"FROM tblServices")
	
	if 'servicename' in request.POST and 'servicecost' in request.POST:
		name = request.POST.get('servicename')
		cost = request.POST.get('servicecost')
                service = Services(name, cost)
                DBSession.add(service)
        #	serviceAdd = DBSession.execute(\
	#	"INSERT INTO tblServices (serviceName, serviceCost) "+\
	#	"VALUES ('" + name + "', '" + cost + "' )")
	return {'project': 'orange_system', 'serviceList': serviceList}
    
@view_config(route_name='part', renderer='templates/partTemplate.pt')
def part_view(request):
	partList = None
	partAdd = None
	partList = DBSession.execute(\
	"SELECT * "+\
	"FROM tblParts")
	
	if 'partname' in request.POST and 'partcost' in request.POST:
		name = request.POST.get('partname')
		cost = request.POST.get('partcost')
		partAdd = DBSession.execute(\
		"INSERT INTO tblParts (partName, partCost) "+\
		"VALUES ('" + name + "', '" + cost + "' )")
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


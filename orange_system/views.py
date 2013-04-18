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
    # We first need to check if the POST data actually exists.  Checking if a name is #in# the post data will pass
    # as long as the request method is POST.
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
                # If we're in add mode, AKA the add customer button is in post, we want to process this block.
                # The reason this works here is because of the chameleon syntax that's causing btnAdd to only be rendered in HTML
                # in add mode, vice versa for btnEdit.  Because of that, we can check for the presence of these names in our POST.
                if 'btnAdd' in request.POST:
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
                elif 'btnEdit' in request.POST:    
                    # We're in edit mode if we get here, so let's go ahead and process information for the update.
                    # Let's start by checking for the information to be stored in tblCustomers
                    if request.POST['firstname'] and request.POST['lastname'] \
                         and request.POST['address'] and request.POST['city'] \
                         and request.POST['state'] and request.POST['zipcode']:
                        # If so then we update, starting with assigning our local customer.
                        newCust = DBSession.query(Customers).filter(Customers.customerID == request.POST['customerID']).one()
                        # Now we need to update the values of the object before we commit.
                        newCust.firstName = request.POST['firstname']
                        newCust.lastName = request.POST['lastname']
                        newCust.address = request.POST['address']
                        newCust.city = request.POST['city']
                        newCust.stateCode = request.POST['state']
                        newCust.zipCode = request.POST['zipcode'] 
                        # Here's the magical part.  When we add this customer, SQLAlchemy will know to use an update instead if the customer
                        # already exists.
                        DBSession.add(newCust)
                    
                    # So now we need to process contact information ie; phone numbers and email addresses.
                    if 'email1' in request.POST:
                        # Basically, our customer has an email, so if we're in here then we're checking the email1 field.
                        # By nesting this if here, we can assure we will not get a name error when we check email1.
                        if request.POST['email1']:
                            email1 = DBSession.query(Email).filter(Email.emailID == request.POST['emailID1']).one()
                            email1.emailAddress = request.POST['email1']
                            email1.emailType = request.POST['emailtype1']
                            DBSession.add(email1)
                    if 'email2' in request.POST:
                        if request.POST['email2']:
                            email2 = DBSession.query(Email).filter(Email.emailID == request.POST['emailID2']).one()
                            email2.emailAddress = request.POST['email2']
                            email2.emailType = request.POST['emailtype2']
                    if 'email3' in request.POST:
                        if request.POST['email3']:
                            email3 = DBSession.query(Email).filter(Email.emailID == request.POST['emailID3']).one()
                            email3.emailAddress = request.POST['emailtype3']
                            email3.emailType = request.POST['emailtype2']
                    if 'phone1' in request.POST:
                        if request.POST['phone1']:
                            phone1 = DBSession.query(Phone).filter(Phone.phoneID == request.POST['phoneID1']).one()
                            phone1.phoneNumber = request.POST['phone1']
                            phone1.phoneType = request.POST['phonetype1']
                    if 'phone2' in request.POST:
                        if request.POST['phone2']:
                            phone2 = DBSession.query(Phone).filter(Phone.phoneID == request.POST['phoneID2']).one()
                            phone2.phoneNumber = request.POST['phone2']
                            phone2.phoneType = request.POST['phonetype2']
                    if 'phone3' in request.POST:
                        if request.POST['phone3']:
                            phone3 = DBSession.query(Phone).filter(Phone.phoneID == request.POST['phoneID3']).one()
                            phone3.phoneNumber = request.POST['phone3']
                            phone3.phoneType = request.POST['phonetype3']

                        
                   
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
    
@view_config(route_name='order', renderer='templates/orderTemplate.pt')
def order_view(request):
	orders = DBSession.query(Orders).all()
	# We need to fetch service and part names for the select boxes
	services = DBSession.query(Services).all()
	parts = DBSession.query(Parts).all()
	return {'project': 'orange_system', 'orders': orders, 'services':services, 'parts':parts}
    
@view_config(route_name='service', renderer='templates/serviceTemplate.pt')
def service_view(request):
	serviceList = None
	serviceAdd = None
	name = None
	cost = None
	serviceList = DBSession.query(Services).all()
	#serviceList = DBSession.execute(\
	#"SELECT serviceID, serviceName, serviceCost "+\
	#"FROM tblServices")
	if request.POST:
		if request.POST['servicename'] and request.POST['servicecost']:
			name = request.POST['servicename']
			cost = request.POST['servicecost']
			service = Services(name, cost)
			print service.serviceName
			if service:
				DBSession.add(service)
        #	serviceAdd = DBSession.execute(\
		#	"INSERT INTO tblServices (serviceName, serviceCost) "+\
		#	"VALUES ('" + name + "', '" + cost + "' )")
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
		#	partAdd = DBSession.execute(\
		#	"INSERT INTO tblParts (partName, partCost) "+\
		#	"VALUES ('" + name + "', '" + cost + "' )")
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


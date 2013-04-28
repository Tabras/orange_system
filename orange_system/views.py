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
    ServicesByOrder,
    PartsByOrder,
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
	customer = None
	orderServicesList = None
	orderServicesFull = None
	orderPartsList = None
	orderPartsFull = None
	serviceTotal = {'servicesTotal': 0}
	partTotal = {'partsTotal': 0}
	orderTotal = {'ordersTotal': 0}
	
	# looking for the order id to be passed
	if 'orderID' in request.GET:
		
		# here we are finding the order associated with the id that was just passed from the order page
		order = DBSession.query(Orders).filter(Orders.orderID == request.GET['orderID']).first()

		# we will also find all the services and parts associated with the selected order
		orderServicesList = DBSession.execute(\
		"SELECT s.serviceID, s.serviceName, s.serviceCost "+\
		"FROM tblServicesByOrder AS so "+\
		"INNER JOIN tblServices AS s "+\
		"ON so.serviceID = s.serviceID "+\
		"WHERE so.orderID = " + request.GET['orderID']).fetchall()
		orderServicesFull = [row for row in orderServicesList]
		
		orderPartsList = DBSession.execute(\
		"SELECT p.partID, p.partName, p.partCost "+\
		"FROM tblPartsByOrder AS po "+\
		"INNER JOIN tblParts AS p "+\
		"ON po.partID = p.partID "+\
		"WHERE po.orderID = " + request.GET['orderID']).fetchall()
		orderPartsFull = [row for row in orderPartsList]
		
		# this bit of code uses the custID referenced from the order object made earlier to find the customer name for display
		customer = DBSession.query(Customers).filter(Customers.customerID == order.custID).first()
		
		# now we are going to fill a dictionary so we can find the service total
		for i in range(len(orderServicesList)):
			serviceTotal['servicesTotal'] += float(orderServicesList[i].serviceCost)
			
		# and do the same for parts
		for i in range(len(orderPartsList)):
			partTotal['partsTotal'] += float(orderPartsList[i].partCost)
			
		# finally we calculate the order total
		orderTotal['ordersTotal'] = serviceTotal['servicesTotal'] + partTotal['partsTotal']
		
		# because this was the most logical place to update the order price we will overwrite it here
		order.orderCost = orderTotal['ordersTotal']
		print "<---ORDER COST OVERWRITTEN--->"
		DBSession.add(order)
		
		# finally, because we just updated the orders we need to pull a fresh version to pass to the orderTemplate
		order = DBSession.query(Orders).filter(Orders.orderID == request.GET['orderID']).first()
			
	# Then we return each of the objects containing data that we built to the order_view
	return {'project': 'orange_system', 
	'orders': orders, 
	'order': order, 
	'services': services, 
	'parts': parts, 
	'progress': progress,
	'orderServicesFull': orderServicesFull,
	'orderPartsFull': orderPartsFull,
	'serviceTotal': serviceTotal,
	'partTotal': partTotal,
	'orderTotal': orderTotal,
	'customer': customer,
	}
	
@view_config(route_name='addOrder', request_method="POST", renderer='json')
def addOrder_view(request):
    order = Orders(
    request.POST['custID'],
    request.POST['modelName'],
    request.POST['orderNotes'],
    "0.00", # This is a placeholder for orderCost since there is no cost yet
    request.POST['entryDate'],
    " ", # This is a placeholder for completionDate since theres no data yet
    request.POST['progressDescription'])
 
    DBSession.add(order)
    return {}
    
@view_config(route_name='updateOrder', request_method='POST', renderer='json')
def updateOrder_view(request):
	order = DBSession.query(Orders).filter(Orders.orderID == request.POST['orderID']).first()
	order.orderID = request.POST['orderID']
	order.custID = request.POST['custID']
	order.modelName = request.POST['modelName']
	order.orderNotes = request.POST['orderNotes']
	order.entryDate = request.POST['entryDate']
	order.completionDate = request.POST['completionDate']
	order.progressDescription = request.POST['progressDescription']
	print "DEBUGGER!"
	DBSession.add(order)
	return{}
	
    
@view_config(route_name='deleteOrder', request_method='POST', renderer='json')
def deleteOrder_view(request):
	print "<---ORDER DELETE DEBUG--->"
	print request.POST['formData[0][value]']
	
	orderID = request.POST['formData[0][value]']
	DBSession.query(Orders).filter(Orders.orderID == orderID).delete()
	return {}
	
@view_config(route_name='updateOrderServices', request_method='POST', renderer='json')
def updateOrderServices_view(request):
	service = None
	serviceToOrder = None
	
	service = DBSession.execute(\
	"SELECT serviceID "+\
	"FROM tblServices "+\
	"WHERE serviceName = " + "'" +request.POST['serviceName'] +"'").fetchone()
	
	serviceToOrder = ServicesByOrder(service['serviceID'], request.POST['orderID'])
	
	DBSession.add(serviceToOrder)
	return{}
	
@view_config(route_name='updateOrderParts', request_method='POST', renderer='json')
def updateOrderParts_view(request):
	part = None
	partToOrder = None

	part = DBSession.execute(\
	"SELECT partID "+\
	"FROM tblParts "+\
	"WHERE partName = " + "'" +request.POST['partName'] +"'").fetchone()
	
	partToOrder = PartsByOrder(part['partID'], request.POST['orderID'])
	
	DBSession.add(partToOrder)
	return{}
	
@view_config(route_name='deleteOrderParts', request_method='POST', renderer='json')
def deleteOrderParts_view(request):
	print "<---ORDER PART DELETE DEBUG--->"
	print request.POST
	partID = request.POST['partID[0][value]']
	print partID
	#orderID = request.POST['orderID[0][value]']
	#DBSession.query(PartsByOrder).filter(PartsByOrder.partID == partID, PartsByOrder.orderID == orderID).delete()
	print "COMPLETE"
	return{}
    
@view_config(route_name='service', renderer='templates/serviceTemplate.pt')
def service_view(request):
	service = None
	services = None
	
	print "<---SERVICE DEBUG--->"
	services = DBSession.query(Services).all()
	
	print "<---SERVICE ID PULLED--->"
	if 'serviceID' in request.GET:
		# here we are finding the service associated with the id that was just passed from the service page
		service = DBSession.query(Services).filter(Services.serviceID == request.GET['serviceID']).first()
		
	# then we return each of the objects containing  data that we built to the service_view
	print "<---SERVICE VIEW RETURN--->"
	return {'project': 'orange_system', 
	'services': services,
	'service': service,
	}
	
@view_config(route_name='addService', request_method='POST', renderer='json')
def addService_view(request):
	service = None
	service = Services(
	request.POST['serviceName'], 
	request.POST['serviceCost'])
	print "<---SERVICE ADDED--->"
	DBSession.add(service)
	return {}
	
@view_config(route_name='updateService', request_method='POST', renderer='json')
def updateService_view(request):
	service = None
	service = DBSession.query(Services).filter(Services.serviceID == request.POST['serviceID']).first()
	service.serviceID = request.POST['serviceID']
	service.serviceName = request.POST['serviceName']
	service.serviceCost = request.POST['serviceCost']
	print "<---SERVICE UPDATED--->"
	DBSession.add(service)
	return {}
	
@view_config(route_name='deleteService', request_method='POST', renderer='json')
def deleteService_view(request):
	print "<---SERVICE DELETE DEBUG--->"
	print request.POST['formData[0][value]']
	
	serviceID = request.POST['formData[0][value]']
	
	print "<---SERVICE DELETED--->"
	DBSession.query(Services).filter(Services.serviceID == serviceID).delete()
	return {}
    
@view_config(route_name='part', renderer='templates/partTemplate.pt')
def part_view(request):
	part = None
	parts = None
	parts = DBSession.query(Parts).all()
	
	if 'partID' in request.GET:
		# here we are finding the part associated with the id that was just passed from the part page
		part = DBSession.query(Parts).filter(Parts.partID == request.GET['partID']).first()
		
    # then we return each of the objects containing  data that we built to the part_view
	return {'project': 'orange_system', 
	'parts': parts,
	'part': part,
	}
	
@view_config(route_name='addPart', request_method='POST', renderer='json')
def addPart_view(request):
	part = None
	part = Parts(
	request.POST['partName'], 
	request.POST['partCost'])
	
	DBSession.add(part)
	return {}
	
@view_config(route_name='updatePart', request_method='POST', renderer='json')
def updatePart_view(request):
	part = None
	part = DBSession.query(Parts).filter(Parts.partID == request.POST['partID']).first()
	part.partID = request.POST['partID']
	part.partName = request.POST['partName']
	part.partCost = request.POST['partCost']
	
	DBSession.add(part)
	return {}
	
@view_config(route_name='deletePart', request_method='POST', renderer='json')
def deletePart_view(request):
	print "<---PART DELETE DEBUG--->"
	print request.POST['formData[0][value]']
	
	partID = request.POST['formData[0][value]']
	DBSession.query(Parts).filter(Parts.partID == partID).delete()
	print "THIS ACTUALLY RAN"
	return {}
	
@view_config(route_name='report', renderer='templates/reportTemplate.pt')
def report_view(request):
    return {'project': 'orange_system'}
    
@view_config(route_name='checkout', renderer='templates/checkoutTemplate.pt')
def checkout_view(request):
	orderCheckout = DBSession.query(Orders).filter(Orders.progressDescription == "Completed").all()
	return {'project': 'orange_system', 'orderCheckout': orderCheckout}
    
@view_config(route_name='todo', renderer='templates/todoTemplate.pt')
def todo_view(request):
    # We want to pull in any orders that are not finished yet.  We need
    # group_concat again for this one so we can get a concatenated field containing
    # all parts/services to the order we use fetchall() here to bypass
    # the ORM and obtain our result as a generic list.  You'll see why down further.
    todoList = DBSession.execute(\
    "SELECT o.orderID, o.custID, o.modelName, o.orderNotes, o.orderCost, o.entryDate, "+\
    "o.progressDescription, "+\
    "group_concat(DISTINCT p.partID) AS partsOnOrder, "+\
    "group_concat(DISTINCT s.serviceID) AS servicesOnOrder "+\
    "FROM tblOrders AS o "+\
    "LEFT JOIN tblPartsByOrder AS p ON o.orderID = p.orderID "+\
    "LEFT JOIN tblServicesByOrder AS s ON o.orderID = p.orderID "+\
    "WHERE o.progressDescription != 'Completed' "+\
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


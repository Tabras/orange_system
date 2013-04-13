from pyramid.response import Response
from pyramid.view import view_config
import locale
from sqlalchemy.exc import DBAPIError
from sqlalchemy import *

from pyramid.httpexceptions import HTTPFound
from .models import (
    DBSession,
    Customers,
    Email,
    Phone,
    )
DBSession.execute('SELECT group_concat(emailAddress) FROM tblEmail')
@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'orange_system'}

@view_config(route_name='search', renderer='templates/searchTemplate.pt')
def search_view(request):
    result = None
    if 'q' in request.GET:
        search = request.GET.get('q')
        result = DBSession.execute(\
        "SELECT c.id, c.firstName, c.lastName, c.address, c.city, c.stateCode,"+\
        " c.zipCode, group_concat(DISTINCT e.emailAddress) AS 'emails', "+\
        "group_concat(DISTINCT p.phoneNumber) AS 'Phone Number' "+\
        "FROM tblCustomers AS c "+\
        "JOIN tblEmail AS e ON c.id = e.custID "+\
        "JOIN tblPhone AS p ON c.id = p.custID "+\
        "WHERE c.firstName LIKE '%" + search + "%' OR "+\
        "c.lastName LIKE '%" + search + "%' OR "+\
        "c.address LIKE '%" + search + "%' OR "+\
        "c.city LIKE '%" + search + "%' OR "+\
        "c.stateCode LIKE '%" + search + "%' OR "+\
        "c.zipCode LIKE '%" + search + "%' OR "+\
        "e.emailAddress LIKE '%" + search + "%' OR "+\
        "p.phoneNumber LIKE '%" + search + "%' "+\
        "GROUP BY c.id")
    return {'project': 'orange_system', 'result': result}

@view_config(route_name='search', request_param="q=''")
def search_display(request):
    return {}

@view_config(route_name='customer', renderer='templates/customerTemplate.pt')
def customer_view(request):
    # placeholder ID until the page is functional
    custID = 1
    customerInfo = DBSession.query(Customers).filter(Customers.id == custID).first()
    customerEmail = DBSession.query(Email).filter(Email.custID == custID).all()
    customerPhone = DBSession.query(Phone).filter(Phone.custID == custID).all()
    
    return {'project': 'orange_system', 'customerInfo': customerInfo, 'customerEmail': customerEmail, 'customerPhone': customerPhone}
    
@view_config(route_name='order', renderer='templates/orderTemplate.pt')
def order_view(request):
    return {'project': 'orange_system'}
    
@view_config(route_name='service', renderer='templates/serviceTemplate.pt')
def service_view(request):
    return {'project': 'orange_system'}
    
@view_config(route_name='part', renderer='templates/partTemplate.pt')
def part_view(request):
    return {'project': 'orange_system'}
    
@view_config(route_name='report', renderer='templates/reportTemplate.pt')
def report_view(request):
    return {'project': 'orange_system'}
    
@view_config(route_name='todo', renderer='templates/todoTemplate.pt')
def todo_view(request):
    return {'project': 'orange_system'}
    
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


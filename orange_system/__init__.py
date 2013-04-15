from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.add_route('search', '/Search')
    config.add_route('customer','/Customers/add')
    config.add_route('editCust','/Customers/edit')
    config.add_route('order','/Orders')
    config.add_route('service','/Services')
    config.add_route('part','/Parts')
    config.add_route('report','/Reports')
    config.add_route('todo','/ToDo')
    config.scan()
    return config.make_wsgi_app()

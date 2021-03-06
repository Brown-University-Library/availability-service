# -*- coding: utf-8 -*-

"""
Helper for availability_service.availability_app
"""

import datetime, os
# from availability_service.utils import backend
from availability_service.utils import z3950_wrapper
from werkzeug.contrib.cache import FileSystemCache


class HandlerHelper( object ):
    """ Helpers for main api route: availability_service.availability_app.handler() """

    def __init__( self, log ):
        self.log = log
        self.HOST = unicode( os.getenv(u'availability_HOST') )
        self.PORT = unicode( os.getenv(u'availability_PORT') )
        self.DB_NAME = unicode( os.getenv(u'availability_DB_NAME') )
        self.legit_services = [ u'bib', u'isbn', u'issn', u'oclc' ]  # will enhance; possible TODO: load from yaml config file
        self.cache_dir = os.getenv( u'availability_CACHE_DIR' )
        self.cache_minutes = int( os.getenv(u'availability_CACHE_MINUTES') ) * 60  # timeout param requires seconds

    def build_query_dict( self, url, key, value, show_marc_param ):
        """ Query reflector.
            Called by availability_service.availability_app.handler(). """
        start_time = datetime.datetime.now()
        query_dict = {
            u'url': url,
            u'query_timestamp': unicode(start_time),
            u'query_key': key,
            u'query_value': value, }
        if show_marc_param == u'true':
            query_dict[u'show_marc'] = show_marc_param
        return query_dict

    def validate( self, key, value ):
        """ Stub for validation. IP checking another possibility.
            Called by availability_service.availability_app.handler(). """
        message = u'init'
        if key not in self.legit_services:
            message = u'service_id bad'
        if message == u'init':
            message = u'good'
        self.log.debug( u'in utils.app_helper.HandlerHelper.validate(); message, %s' % message )
        return message

    def build_response_dict( self, key, value, show_marc_param ):
        """ Handler for cached z39.50 call and response.
            Called by availability_service.availability_app.handler(). """
        assert type(value) == unicode
        cache = FileSystemCache( self.cache_dir, threshold=500, default_timeout=self.cache_minutes, mode=0664 )  # http://werkzeug.pocoo.org/docs/0.9/contrib/cache/
        cache_key = u'%s_%s_%s' % ( key, value, show_marc_param )
        response_dict = cache.get( cache_key )
        if response_dict is None:
            self.log.debug( u'in utils.app_helper.HandlerHelper.build_response_dict(); _not_ using cache.' )
            response_dict = self.query_josiah( key, value, show_marc_param )
            cache.set( cache_key, response_dict )
        return response_dict

    def query_josiah( self, key, value, show_marc_param ):
        """ Perform actual query.
            Called by self.build_response_dict(). """
        marc_flag = True if show_marc_param == u'true' else False
        srchr = z3950_wrapper.Searcher(
            HOST=self.HOST, PORT=self.PORT, DB_NAME=self.DB_NAME, logger=self.log, connect_flag=True
            )
        item_list = srchr.search( key, value, marc_flag )
        srchr.close_connection()
        return {
            u'backend_response': item_list,
            u'response_timestamp': unicode(datetime.datetime.now()) }

    # end class HandlerHelper

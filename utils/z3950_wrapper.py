# -*- coding: utf-8 -*-

"""
Wrapper for z3950 library call & data-extraction.
Resources:
- z3950 library docs, http://www.panix.com/~asl2/software/PyZ3950/zoom.html
- list of record formats,  http://lists.indexdata.dk/pipermail/zoom/2003-November/000547.html
"""

import logging, os, pprint, sys
from PyZ3950 import zoom  # fork, git+https://github.com/Brown-University-Library/PyZ3950.git
from pymarc import Record  # pymarc==3.0.2


class Searcher( object ):

    def __init__( self, logger ):
        self.HOST = unicode( os.getenv(u'availability_HOST') )
        self.PORT = unicode( os.getenv(u'availability_PORT') )
        self.DB_NAME = unicode( os.getenv(u'availability_DB_NAME') )
        self.logger = logger
        self.connection = None

    def connect( self ):
        conn = zoom.Connection(
            self.HOST,
            int(self.PORT),
            databaseName=self.DB_NAME,
            preferredRecordSyntax=u'OPAC',  # Getting records in "opac" format. (Others were not more helpful.)
            charset=u'utf-8',
            )
        self.connection = conn
        return

    def close_connection( self ):
        self.logger.debug( 'in z3950_wrapper.Searcher.close_connection(); closing connection.')
        self.connection.close()

    def search( self, key, value, marc_flag=False ):
        """ Convenience function. """
        try:
            qstring = self.build_qstring( key, value )
            qobject = self.build_qobject( qstring )
            resultset = self.connection.search( qobject )
            item_list = self.process_resultset( resultset, marc_flag )  # marc_flag typically False
            return item_list
        except Exception as e:
            self.close_connection()
            error_dict = self.make_error_dict()
            self.logger.error( u'in z3950_wrapper.Searcher.search(); error-info, `%s`' % pprint.pformat(error_dict) )

    def build_qstring( self, key, value ):
        if key == u'bib':
            key = u'id'
        dct = {
            u'isbn': u'@attr 1=7',
            u'issn': u'@attr 1=8',
            u'id': u'@attr 1=12',
            u'oclc': u'@attr 1=1007', }
        qstring = u'%s %s' % ( dct[key], value )
        self.logger.debug( 'in z3950_wrapper.Searcher.build_qstring(); qstring, `%s`' % qstring )
        return qstring

    def build_qobject( self, qstring ):
        qobject = zoom.Query(
            u'PQF'.encode(u'utf-8'),
            qstring.encode(u'utf-8')
            )
        self.logger.debug( u'in z3950_wrapper.Searcher.build_qobject(); type(qobject), `%s`' % type(qobject) )
        self.logger.debug( u'in z3950_wrapper.Searcher.build_qobject(); pprint.pformat(qobject), `%s`' % pprint.pformat(qobject) )
        return qobject

    def inspect_resultset( self, resultset ):
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(resultset), `%s`' % pprint.pformat(resultset) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(dir(resultset)), `%s`' % pprint.pformat(dir(resultset)) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(resultset.__dict__), `%s`' % pprint.pformat(resultset.__dict__) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(len(resultset)), `%s`' % pprint.pformat(len(resultset)) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(resultset[0]), `%s`' % pprint.pformat(resultset[0]) )
        rec = resultset[0]
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(dir(rec)), `%s`' % pprint.pformat(dir(rec)) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(rec.__dict__), `%s`' % pprint.pformat(rec.__dict__) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(rec.data), `%s`' % pprint.pformat(rec.data) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(rec.data.bibliographicRecord), `%s`' % pprint.pformat(rec.data.bibliographicRecord) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(rec.data.bibliographicRecord.encoding), `%s`' % pprint.pformat(rec.data.bibliographicRecord.encoding) )
        ## marc
        pm_rec = Record( data=rec.data.bibliographicRecord.encoding[1] )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(pm_rec), `%s`' % pprint.pformat(pm_rec) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(dir(pm_rec)), `%s`' % pprint.pformat(dir(pm_rec)) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(pm_rec.__dict__), `%s`' % pprint.pformat(pm_rec.__dict__) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(pm_rec.as_dict()), `%s`' % pprint.pformat(pm_rec.as_dict()) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(pm_rec.title()), `%s`' % pprint.pformat(pm_rec.title()) )
        ## holdings
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(rec.data.holdingsData), `%s`' % pprint.pformat(rec.data.holdingsData) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(rec.data.holdingsData[0]), `%s`' % pprint.pformat(rec.data.holdingsData[0]) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(rec.data.holdingsData[0][0]), `%s`' % pprint.pformat(rec.data.holdingsData[0][0]) )
        self.logger.debug( u'in z3950_wrapper.Searcher.inspect_resultset, pprint.pformat(rec.data.holdingsData[0][1].callNumber, `%s`' % pprint.pformat(rec.data.holdingsData[0][1].callNumber) )
        return

    def process_resultset( self, resultset, marc_flag=False ):
        """ Iterates through resultset, extracting from marc-data and holdings-data. """
        item_list = []
        for result in resultset:
            ## start w/marc
            marc_record_object = Record( data=result.data.bibliographicRecord.encoding[1] )
            item_entry = self.process_marc_data( marc_record_object, marc_flag )
            ## add holdings
            holdings_record_data = result.data.holdingsData
            item_entry[u'holdings_data'] = self.process_holdings_data( holdings_record_data )
            item_list.append( item_entry )
        self.logger.debug( u'in z3950_wrapper.Searcher.process_resultset, pprint.pformat(item_list), `%s`' % pprint.pformat(item_list) )
        return item_list

    def process_holdings_data( self, holdings_data ):
        record_holdings_data = []
        for holdings_entry in holdings_data:
            entry = {}
            holdings_object = holdings_entry[1]
            entry[u'callNumber'] = holdings_object.callNumber
            entry[u'localLocation'] = holdings_object.localLocation
            entry[u'publicNote'] = holdings_object.publicNote
            record_holdings_data.append( entry )
        self.logger.debug( u'in z3950_wrapper.Searcher.process_holdings_data, pprint.pformat(record_holdings_data), `%s`' % pprint.pformat(record_holdings_data) )
        return record_holdings_data

    def process_marc_data( self, marc_record_object, marc_flag ):
        marc_dict = marc_record_object.as_dict()
        item_entry = {}
        if marc_flag:
            item_entry[u'raw_marc'] = marc_dict
        item_entry[u'title'] = marc_record_object.title()
        item_entry[u'callnumber'] = self.make_marc_callnumber( marc_dict )
        item_entry[u'itemid'] = self.make_marc_itemid( marc_dict )
        item_entry[u'item_barcode'] = self.make_marc_barcode( marc_dict )
        item_entry[u'isbn'] = marc_record_object.isbn()
        item_entry[u'lccn'] = self.make_lccn( marc_dict )
        item_entry[u'location'] = self.make_location( marc_dict )
        item_entry[u'bibid'] = self.make_bibid( marc_dict )
        item_entry[u'josiah_bib_url'] = u'%s/record=%s' % ( u'https://josiah.brown.edu', item_entry[u'bibid'][1:-1] )  # removes period & check-digit
        item_entry[u'oclc_brown'] = self.make_oclc_brown( marc_dict )
        self.logger.debug( u'in z3950_wrapper.Searcher.process_marc_data(); pprint.pformat(item_entry), `%s`' % pprint.pformat(item_entry) )
        return item_entry

    def make_marc_callnumber( self, marc_dict ):
        ( callnumber, subfield_callnumber ) = ( u'callnumber_not_available', u'' )
        for field in marc_dict[u'fields']:
            ( key, val ) = field.items()[0]
            if key == u'050' or key == u'090':
                for subfield in field[key][u'subfields']:
                    ( key2, val2 ) = subfield.items()[0]
                    subfield_callnumber = u'%s %s' % (subfield_callnumber, val2)
                callnumber = subfield_callnumber.strip()
                break
        self.logger.debug( u'in z3950_wrapper.Searcher.make_marc_callnumber(); callnumber, `%s`' % callnumber )
        return callnumber

    def make_marc_itemid( self, marc_dict ):
        itemid = u'itemid_not_available'
        for field in marc_dict[u'fields']:
            ( key, val ) = field.items()[0]
            if key == u'945':
                for subfield in field[key][u'subfields']:
                    ( key2, val2 ) = subfield.items()[0]
                    if key2 == u'y':
                        itemid = val2
                        break
        self.logger.debug( u'in z3950_wrapper.Searcher.make_marc_itemid(); itemid, `%s`' % itemid )
        return itemid

    def make_marc_barcode( self, marc_dict ):
        barcode = []
        for field in marc_dict[u'fields']:
            ( key, val ) = field.items()[0]
            if key == u'945':
                for subfield in field[key][u'subfields']:
                    ( key2, val2 ) = subfield.items()[0]
                    if key2 == u'i':
                        barcode.append( val2.replace(u' ', u'') )
        self.logger.debug( u'in z3950_wrapper.Searcher.make_marc_barcode(); barcode, `%s`' % barcode )
        return barcode

    def make_lccn( self, marc_dict ):
        lccn = u'lccn_not_available'
        for field in marc_dict[u'fields']:
            ( key, val ) = field.items()[0]
            if key == u'010':
                for subfield in field[key][u'subfields']:
                    ( key2, val2 ) = subfield.items()[0]
                    if key2 == u'a':
                        lccn = val2
                        break
        self.logger.debug( u'in z3950_wrapper.Searcher.make_lccn(); lccn, `%s`' % lccn )
        return lccn

    def make_location( self, marc_dict ):
        location = u'location_not_available'
        for field in marc_dict[u'fields']:
            ( key, val ) = field.items()[0]
            if key == u'945':
                for subfield in field[key][u'subfields']:
                    ( key2, val2 ) = subfield.items()[0]
                    if key2 == u'l':
                        location = val2
                        break
        self.logger.debug( u'in z3950_wrapper.Searcher.make_location(); location, `%s`' % location )
        return location.strip()

    def make_bibid( self, marc_dict ):
        bibid = u'bibid_not_available'
        for field in marc_dict[u'fields']:
            ( key, val ) = field.items()[0]
            if key == u'907':
                for subfield in field[key][u'subfields']:
                    ( key2, val2 ) = subfield.items()[0]
                    if key2 == u'a':
                        bibid = val2
                        break
        self.logger.debug( u'in z3950_wrapper.Searcher.make_bibid(); bibid, `%s`' % bibid )
        return bibid

    def make_oclc_brown( self, marc_dict ):
        oclc = u'oclc_not_available'
        for field in marc_dict[u'fields']:
            ( key, val ) = field.items()[0]
            if key == u'001':
                oclc = val
                break
        self.logger.debug( u'in z3950_wrapper.Searcher.make_oclc_brown(); oclc, `%s`' % oclc )
        return oclc

    def make_error_dict( self ):
        error_dict = {
            u'error-type': sys.exc_info()[0],
            u'error-message': sys.exc_info()[1],
            u'line-number': sys.exc_info()[2].tb_lineno
            }
        return error_dict

    # end class Searcher()
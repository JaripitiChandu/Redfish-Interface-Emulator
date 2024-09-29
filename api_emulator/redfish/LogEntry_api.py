# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# LogEntry API File

"""
Collection API:  GET
Singleton  API:  GET, POST
"""

import g

import sys, traceback
import logging, json
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

from g import INTERNAL_SERVER_ERROR

INDICES = [1,3,5]

# LogEntry Singleton API
class LogEntryAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('LogEntryAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

       # HTTP GET
    def get(self, ident, ident1, ident2):
        logging.info('LogEntryAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1 , ident2):
        logging.info('LogEntryAPI PUT called')
        return 'PUT is not a supported command for LogEntryAPI', 405

    # HTTP POST
    def post(self, ident, ident1, ident2):
        logging.info('LogEntryAPI POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1, ident2):
        logging.info('LogEntryAPI PATCH called')
        return 'PATCH is not a supported command for LogEntryAPI', 405

    # HTTP DELETE
    def delete(self, ident, ident1):
        logging.info('LogEntryAPI DELETE called')
        return 'DELETE is not a supported command for LogEntryAPI', 405

# LogEntry Collection API
class LogEntryCollectionAPI(Resource):

    def __init__(self):
        logging.info('LogEntryCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.id': " ",
            '@odata.type': '#LogEntryCollection.LogEntryCollection',
            '@odata.context': self.rb + '$metadata#LogEntryCollection.LogEntryCollection',
            'Name': 'Log Service Collection',
            "Members": [],
            "Members@odata.count": 0,
        }

    # HTTP GET
    def get(self,ident,ident1):
        logging.info('LogEntryCollectionAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            passed, output = g.get_collection_from_bucket_hierarchy(bucket_hierarchy, INDICES[:-1])
            if not passed:
                return output, 404
            self.config["@odata.id"] = "/redfish/v1/Managers/<string:ident>/LogServices/<string:ident1>/Entries".format(ident)
            self.config['Members'] = [{'@odata.id': x} for x in output]
            self.config["Members@odata.count"] = len(output)
            resp = self.config, 200
            
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self,ident):
        logging.info('LogEntryCollectionAPI PUT called')
        return 'PUT is not a supported command for LogEntryCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self,ident):
        logging.info('LogEntryCollectionAPI POST called')
        return 'POST is not a supported command for LogEntryCollectionAPI', 405

    # HTTP PATCH
    def patch(self):
        logging.info('LogEntryCollectionAPI PATCH called')
        return 'PATCH is not a supported command for LogEntryCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('LogEntryCollectionAPI DELETE called')
        return 'DELETE is not a supported command for LogEntryCollectionAPI', 405



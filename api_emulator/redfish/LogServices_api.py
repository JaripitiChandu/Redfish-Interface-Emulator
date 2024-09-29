# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# LogService API File

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

members = {}
INDICES = [1,3]

# LogService Singleton API
class LogServiceAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('LogServiceAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident, ident1):
        logging.info('LogServiceAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1):
        logging.info('LogServiceAPI PUT called')
        return 'PUT is not a supported command for LogServiceAPI', 405

    # HTTP POST
    def post(self, ident, ident1):
        logging.info('LogServiceAPI POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1):
        logging.info(self.__class__.__name__ + ' PATCH called')
        patch_data = request.get_json(force=True)
        logging.info(f"Payload = {patch_data}")
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.patch_bucket_value(bucket_hierarchy, INDICES, patch_data)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident, ident1):
        logging.info('LogServiceAPI DELETE called')
        return 'DELETE is not a supported command for LogServiceAPI', 405

# LogService Collection API
class LogServiceCollectionAPI(Resource):

    def __init__(self):
        logging.info('LogServiceCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.id': " ",
            '@odata.type': '#LogServiceCollection.LogServiceCollection',
            '@odata.context': self.rb + '$metadata#LogServiceCollection.LogServiceCollection',
            'Name': 'Log Service Collection',
            "Members": [],
            "Members@odata.count": 0,
            "Description": "Collection of LogServices for this Manager"
        }

    # HTTP GET
    def get(self,ident):
        logging.info('LogServiceCollectionAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            passed, output = g.get_collection_from_bucket_hierarchy(bucket_hierarchy, INDICES[:-1])
            if not passed:
                return output, 404
            self.config["@odata.id"] = "/redfish/v1/Manager/{}/LogServices".format(ident)
            self.config['Members'] = [{'@odata.id': x} for x in output]
            self.config["Members@odata.count"] = len(output)
            resp = self.config, 200
            
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self,ident):
        logging.info('LogServiceCollectionAPI PUT called')
        return 'PUT is not a supported command for LogServiceCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self,ident):
        logging.info('LogServiceCollectionAPI POST called')
        return 'POST is not a supported command for LogServiceCollectionAPI', 405

    # HTTP PATCH
    def patch(self):
        logging.info('LogServiceCollectionAPI PATCH called')
        return 'PATCH is not a supported command for LogServiceCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('LogServiceCollectionAPI DELETE called')
        return 'DELETE is not a supported command for LogServiceCollectionAPI', 405



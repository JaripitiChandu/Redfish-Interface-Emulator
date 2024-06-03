# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# NetworkDeviceFunctions API File

"""
Collection API:  GET
Singleton  API:  GET, POST
"""

import g
from g import INTERNAL_SERVER_ERROR as INTERNAL_ERROR

import json
import sys, traceback
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

members = {}
BNAME = 'NetworkDeviceFunctions'
INDICES = [1,3,5]


# NetworkDeviceFunctions Singleton API
class NetworkDeviceFunctionsAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('NetworkDeviceFunctionsAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident, ident1, ident2):
        logging.info('NetworkDeviceFunctionsAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)    
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1 , ident2):
        logging.info('NetworkDeviceFunctionsAPI PUT called')
        return 'PUT is not a supported command for NetworkDeviceFunctionsAPI', 405

    # HTTP POST
    def post(self, ident, ident1, ident2):
        logging.info('NetworkDeviceFunctionsAPI POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1, ident2):
        logging.info(self.__class__.__name__ + ' PATCH called')
        patch_data = request.get_json(force=True)
        logging.info(f"Payload = {patch_data}")
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.patch_bucket_value(bucket_hierarchy, INDICES, patch_data)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident, ident1):
        logging.info('NetworkDeviceFunctionsAPI DELETE called')
        try:
            # Find the entry with the correct value for Id
            resp = 404
            if ident in members:
                del(members[ident])
                resp = 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp


# NetworkDeviceFunctions Collection API
class NetworkDeviceFunctionsCollectionAPI(Resource):

    def __init__(self):
        logging.info('NetworkDeviceFunctionsCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.id': " ",
            '@odata.type': '#NetworkDeviceFunctionsCollection.NetworkDeviceFunctionsCollection',
            '@odata.context': self.rb + '$metadata#NetworkDeviceFunctionsCollection.NetworkDeviceFunctionsCollection',
            'Name': 'NetworkDeviceFunctions Collection',
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self,ident,ident1):
        logging.info('NetworkDeviceFunctionsCollectionAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            passed, output = g.get_collection_from_bucket_hierarchy(bucket_hierarchy, INDICES[:-1])
            if not passed:
                return output, 404
            self.config["@odata.id"] = "/redfish/v1/Chassis/{}/NetworkAdapters/{}/NetworkDeviceFunctions".format(ident,ident1)
            self.config["Members"] = [{'@odata.id': x} for x in output]
            self.config["Members@odata.count"] = len(output)
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident):
        logging.info('NetworkDeviceFunctionsCollectionAPI PUT called')
        return 'PUT is not a supported command for NetworkDeviceFunctionsCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    def post(self,ident):
        logging.info('NetworkDeviceFunctionsCollectionAPI POST called')
        return 'POST is not a supported command for NetworkDeviceFunctionsCollectionAPI', 405

    # HTTP PATCH
    def patch(self):
        logging.info('NetworkDeviceFunctionsCollectionAPI PATCH called')
        return 'PATCH is not a supported command for NetworkDeviceFunctionsCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('NetworkDeviceFunctionsCollectionAPI DELETE called')
        return 'DELETE is not a supported command for NetworkDeviceFunctionsCollectionAPI', 405


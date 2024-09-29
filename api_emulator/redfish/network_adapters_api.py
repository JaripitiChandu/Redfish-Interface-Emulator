# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# NetworkAdapters API File

"""
Collection API:  GET, POST
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
from .Chassis_api import BNAME as RESOURCE_BNAME
from api_emulator.utils import update_nested_dict

members = {}
BNAME = 'NetworkAdapters'
INDICES = [1,3]


# NetworkAdapters Singleton API
class NetworkAdaptersAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('NetworkAdaptersAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident, ident1):
        logging.info('NetworkAdaptersAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)      
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1):
        logging.info('NetworkAdaptersAPI PUT called')
        return 'PUT is not a supported command for NetworkAdaptersAPI', 405

    # HTTP POST
    # This is an emulator-only POST command that creates new resource
    # instances from a predefined template. The new instance is given
    # the identifier "ident", which is taken from the end of the URL.
    # PATCH commands can then be used to update the new instance.
    def post(self, ident, ident1):
        logging.info(self.__class__.__name__ + ' POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
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
            resp = INTERNAL_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident, ident1):
        logging.info('NetworkAdaptersAPI DELETE called')
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


# NetworkAdapters Collection API
class NetworkAdaptersCollectionAPI(Resource):

    def __init__(self):
        logging.info('NetworkAdaptersCollectionAPI init called')
        self.rb = g.rest_base

        self.config = {
            '@odata.id': " ",
            '@odata.type': '#NetworkAdapterCollection.NetworkAdapterCollection',
            '@odata.context': self.rb + '$metadata#NetworkAdapterCollection.NetworkAdapterCollection',
            'Name': 'NetworkAdapters Collection',
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self,ident):
        logging.info('NetworkAdaptersCollectionAPI GET called')
        try:
            # define the bucket hierarchy for collection
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            # get list of resources
            passed, output = g.get_collection_from_bucket_hierarchy(bucket_hierarchy, INDICES[:-1])
            if not passed:
                return output, 404
            # update the value of config using obtained values
            self.config["@odata.id"] = "/redfish/v1/Chassis/{}/NetworkAdapters".format(ident)
            self.config['Members'] = [{'@odata.id': x} for x in output]
            self.config["Members@odata.count"] = len(output)
            resp = self.config, 200
            
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident):
        logging.info('NetworkAdaptersCollectionAPI PUT called')
        return 'PUT is not a supported command for NetworkAdaptersCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self,ident):
        logging.info('NetworkAdaptersCollectionAPI POST called')
        return 'POST is not a supported command for NetworkAdaptersCollectionAPI', 405

    # HTTP PATCH
    def patch(self):
        logging.info('NetworkAdaptersCollectionAPI PATCH called')
        return 'PATCH is not a supported command for NetworkAdaptersCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('NetworkAdaptersCollectionAPI DELETE called')
        return 'DELETE is not a supported command for NetworkAdaptersCollectionAPI', 405



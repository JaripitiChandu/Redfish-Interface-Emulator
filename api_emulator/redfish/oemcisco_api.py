# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# OemCisco API File

"""
Collection API:  GET
Singleton  API:  GET, POST
"""

import g

import sys, traceback, json
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

from g import INTERNAL_SERVER_ERROR

INDICES = [1,3]

# OemCisco Singleton API
class OemCiscoAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.


    def __init__(self, **kwargs):
        logging.info('OemCiscoAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info('OemCiscoAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info('OemCiscoAPI PUT called')
        return 'PUT is not a supported command for OemCiscoAPI', 405

    # HTTP POST
    def post(self, ident):
        logging.info('OemCiscoAPI POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp


    # HTTP PATCH
    def patch(self, ident):
        logging.info('OemCiscoAPI PATCH called')
        return 'PATCH is not a supported command for OemCiscoAPI', 405

    # HTTP DELETE
    def delete(self, ident):
        logging.info('OemCiscoAPI DELETE called')
        return 'DELETE is not a supported command for OemCiscoAPI', 405



# OemCisco Collection API
class OemCiscoCollectionAPI(Resource):

    def __init__(self):
        logging.info('OemCiscoCollectionAPI init called')
        self.rb = g.rest_base
        bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
        passed, output = g.get_collection_from_bucket_hierarchy(bucket_hierarchy, INDICES[:-1])
        if not passed:
            return output, 404
        self.config = {
            "@odata.id": "/redfish/v1/OemCisco",
            "@odata.type": "#MessageRegistryFileCollection.MessageRegistryFileCollection",
            "@odata.context": "/redfish/v1/$metadata#MessageRegistryFileCollection.MessageRegistryFileCollection",
            "Description": "Registry Repository",
            "Name": "Registry File Collection",
            "Members": [ {'odata.id':x} for x in output],
            "Members@odata.count": 9
        }

    # HTTP GET
    def get(self):
        logging.info('OemCiscoCollectionAPI GET called')
        try:
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info('OemCiscoCollectionAPI PUT called')
        return 'PUT is not a supported command for OemCiscoCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    def post(self):
        logging.info('OemCiscoCollectionAPI POST called')
        return 'POST is not a supported command for OemCiscoCollectionAPI', 405
 
    # HTTP PATCH
    def patch(self):
        logging.info('OemCiscoCollectionAPI PATCH called')
        return 'PATCH is not a supported command for OemCiscoCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('OemCiscoCollectionAPI DELETE called')
        return 'DELETE is not a supported command for OemCiscoCollectionAPI', 405


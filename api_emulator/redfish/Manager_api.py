# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Manager API File

"""
Collection API:  GET
Singleton  API:  GET, POST
"""

import g
from api_emulator.utils import update_nested_dict

import sys, traceback
import logging, json
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

# Resource and SubResource imports
from .templates.Manager import get_Manager_instance

from g import db, INDEX, INTERNAL_SERVER_ERROR

BNAME = b'Managers'
INDICES = [1]

# Manager Singleton API
class ManagerAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('ManagerAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info('ManagerAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info('ManagerAPI PUT called')
        return 'PUT is not a supported command for ManagerAPI', 405

    # HTTP POST
    def post(self, ident):
        logging.info('ManagerAPI POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident):
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
    def delete(self, ident):
        logging.info('ManagerAPI DELETE called')
        return 'DELETE is not a supported command for ManagerAPI', 405


# Manager Collection API
class ManagerCollectionAPI(Resource):

    def __init__(self):
        logging.info('ManagerCollectionAPI init called')
        self.rb = g.rest_base
        bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
        passed, output = g.get_collection_from_bucket_hierarchy(bucket_hierarchy)
        if not passed:
            return output, 404
        
        self.config = {
            '@odata.context': self.rb + '$metadata#ManagerCollection.ManagerCollection',
            '@odata.id': self.rb + 'Managers',
            '@odata.type': '#ManagerCollection.ManagerCollection',
            'Name': 'Manager Collection',
            'Members': [{'@odata.id': x} for x in output],
            'Members@odata.count': len(output)
        }

    # HTTP GET
    def get(self):
        logging.info('ManagerCollectionAPI GET called')
        try:
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info('ManagerCollectionAPI PUT called')
        return 'PUT is not a supported command for ManagerCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self):
        logging.info('ManagerCollectionAPI POST called')
        return 'POST is not a supported command for ManagerCollectionAPI', 405


    # HTTP PATCH
    def patch(self):
        logging.info('ManagerCollectionAPI PATCH called')
        return 'PATCH is not a supported command for ManagerCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('ManagerCollectionAPI DELETE called')
        return 'DELETE is not a supported command for ManagerCollectionAPI', 405

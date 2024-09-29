# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# CiscoFile API File

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
INDICES = [1,4,6,8]

# CiscoFile Singleton API
class CiscoFileAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('CiscoFileAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident, ident1, ident2):
        logging.info('CiscoFileAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1 , ident2):
        logging.info('CiscoFileAPI PUT called')
        return 'PUT is not a supported command for CiscoFileAPI', 405

    # HTTP POST
    def post(self, ident, ident1, ident2):
        logging.info('CiscoFileAPI POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1):
        logging.info('CiscoFileAPI PATCH called')
        return 'PATCH is not a supported command for CiscoFileAPI', 405

    # HTTP DELETE
    def delete(self, ident, ident1):
        logging.info('CiscoFileAPI DELETE called')
        return 'DELETE is not a supported command for CiscoFileAPI', 405


# CiscoFile Collection API
class CiscoFileCollectionAPI(Resource):

    def __init__(self):
        logging.info('CiscoFileCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.id': " ",
            '@odata.type': '#CiscoFileCollection.CiscoFileCollection',
            '@odata.context': self.rb + '$metadata#CiscoFileCollection.CiscoFileCollection',
            'Description': 'Collection of Cisco Internal Storge Partition resources',
            'Name': 'Cisco Internal Storage Partition Collections',
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self,ident,ident1):
        logging.info('CiscoFileCollectionAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            passed, output = g.get_collection_from_bucket_hierarchy(bucket_hierarchy, INDICES[:-1])
            if not passed:
                return output, 404
            self.config["@odata.id"] = "/redfish/v1/Managers/{}/Oem/CiscoInternalStorage/FlexMMC/CiscoPartition/{}/CiscoFile".format(ident,ident1)
            self.config['Members'] = [{'@odata.id': x} for x in output]
            self.config["Members@odata.count"] = len(output)
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self,ident):
        logging.info('CiscoFileCollectionAPI PUT called')
        return 'PUT is not a supported command for CiscoFileCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    def post(self,ident):
        logging.info('CiscoFileCollectionAPI POST called')
        return 'POST is not a supported command for CiscoFileCollectionAPI', 405

    # HTTP PATCH
    def patch(self):
        logging.info('CiscoFileCollectionAPI PATCH called')
        return 'PATCH is not a supported command for CiscoFileCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('CiscoFileCollectionAPI DELETE called')
        return 'DELETE is not a supported command for CiscoFileCollectionAPI', 405


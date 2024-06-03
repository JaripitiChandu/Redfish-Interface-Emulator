# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Chassis API File

"""
Collection API:  GET
Singleton  API:  GET, POST, PATCH, DELETE
"""

import g
from g import INTERNAL_SERVER_ERROR as INTERNAL_ERROR

import sys, traceback, json
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

members = {}
BNAME = 'Chassis'
INDICES = [1]

# Chassis Singleton API
class ChassisAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    demo_schema = {
        "title": "DemoSchema",
        "type": "object",
        "properties": {
            "AssetTag": {
                "type": "string"
            },
            "ChassisType": {
                "enum": [
                    "Rack",
                    "Blade",
                    "Enclosure",
                    "StandAlone",
                    "RackMount",
                    "Card",
                    "Cartridge",
                    "Row",
                    "Pod",
                    "Expansion",
                    "Sidecar",
                    "Zone",
                    "Sled",
                    "Shelf",
                    "Drawer",
                    "Module",
                    "Component",
                    "IPBasedDrive",
                    "RackGroup",
                    "StorageEnclosure",
                    "ImmersionTank",
                    "HeatExchanger",
                    "PowerStrip",
                    "Other"
                ],
                "type": "string"
            },
        },
        # "required": [""]
    }


    def __init__(self, **kwargs):
        logging.info('ChassisAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info('ChassisAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info('ChassisAPI PUT called')
        return 'PUT is not a supported command for ChassisAPI', 405

    # HTTP POST
    # This is an emulator-only POST command that creates new resource
    # instances from a predefined template. The new instance is given
    # the identifier "ident", which is taken from the end of the URL.
    # PATCH commands can then be used to update the new instance.
    def post(self, ident):
        logging.info('ChassisAPI POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    @g.delay_response()
    @g.validate_json(demo_schema)
    def patch(self, ident):
        logging.info('ChassisAPI PATCH called')
        raw_dict = request.get_json(force=True)
        try:
            # Update specific portions of the identified object
            for key, value in raw_dict.items():
                members[ident][key] = value
            resp = members[ident], 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident):
        logging.info('ChassisAPI DELETE called')
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


# Chassis Collection API
class ChassisCollectionAPI(Resource):

    def __init__(self):
        logging.info('ChassisCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.id': self.rb + 'Chassis',
            '@odata.type': '#ChassisCollection.1.0.0.ChassisCollection',
            '@odata.context': self.rb + '$metadata#ChassisCollection.ChassisCollection',
            'Name': 'Chassis Collection',
            "Members": [],
            'Members@odata.count': 0
        }

    # HTTP GET
    def get(self):
        logging.info('ChassisCollectionAPI GET called')
        try:
            # define the bucket hierarchy for collection
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            # get list of resources
            passed, output = g.get_collection_from_bucket_hierarchy(bucket_hierarchy)
            if not passed:
                return output, 404
            # update the value of config using obtained values
            self.config["Members"] = [{'@odata.id': x} for x in output]
            self.config["Members@odata.count"] = len(output)
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info('ChassisCollectionAPI PUT called')
        return 'PUT is not a supported command for ChassisCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    def post(self):
        logging.info('ChassisCollectionAPI POST called')
        return 'POST is not a supported command for ChassisCollectionAPI', 405
 
    # HTTP PATCH
    def patch(self):
        logging.info('ChassisCollectionAPI PATCH called')
        return 'PATCH is not a supported command for ChassisCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('ChassisCollectionAPI DELETE called')
        return 'DELETE is not a supported command for ChassisCollectionAPI', 405


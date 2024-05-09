# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# CiscoInternalStorage API File

"""
Collection API:  GET
Singleton  API:  GET, POST
"""

import g

import sys, traceback
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource
from .Manager_api import members as manager_members

members = {}

INTERNAL_ERROR = 500


# CiscoInternalStorage Singleton API
class CiscoInternalStorageAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('CiscoInternalStorageAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident, ident1):
        logging.info('CiscoInternalStorageAPI GET called')
        try:
            # Find the entry with the correct value for Id
            resp = 404
            if ident in members:
                if ident1 in members[ident]:
                    resp = members[ident][ident1], 200
                else:
                    resp = f"CiscoInternalStorage {ident1} for Manager {ident} not found", 404
            else:
                resp = f"Manager {ident} not found", 404          
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1):
        logging.info('CiscoInternalStorageAPI PUT called')
        return 'PUT is not a supported command for CiscoInternalStorageAPI', 405

    # HTTP POST
    # This is an emulator-only POST command that creates new resource
    # instances from a predefined template. The new instance is given
    # the identifier "ident", which is taken from the end of the URL.
    # PATCH commands can then be used to update the new instance.
    def post(self, ident, ident1):
        logging.info('CiscoInternalStorageAPI POST called')
        try:
            global config
            if ident in manager_members:
                members.setdefault(ident, {})
                if ident1 in members[ident]:
                    return ident1 + " CiscoInternalStorage already exists", 409
                else:
                    members[ident][ident1] = request.json
            else:
                resp = f"Manager {ident} not found", 404
            
            resp = members[ident][ident1], 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1):
        logging.info('CiscoInternalStorageAPI PATCH called')
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
    def delete(self, ident, ident1):
        logging.info('CiscoInternalStorageAPI DELETE called')
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


# CiscoInternalStorage Collection API
class CiscoInternalStorageCollectionAPI(Resource):

    def __init__(self):
        logging.info('CiscoInternalStorageCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.id': " ",
            '@odata.type': '#CiscoInternalStorageCollection.CiscoInternalStorageCollection',
            '@odata.context': self.rb + '$metadata#CiscoInternalStorageCollection.CiscoInternalStorageCollection',
            "Description": "Collection of Cisco Internal Storge resources",
            "Name": "Cisco Internal Storage Collections",
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self,ident):
        logging.info('CiscoInternalStorageCollectionAPI GET called')
        try:
            self.config["@odata.id"] = "/redfish/v1/Manager/{}/Oem/CiscoInternalStorage".format(ident)
            self.config["Members"] = [{'@odata.id': CiscoInternalStorage['@odata.id']} for CiscoInternalStorage in list(members.get(ident, {}).values())]
            self.config["Members@odata.count"] = len(members.setdefault(ident, {}))
            resp = self.config, 200
            
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident):
        logging.info('CiscoInternalStorageCollectionAPI PUT called')
        return 'PUT is not a supported command for CiscoInternalStorageCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self,ident):
        logging.info('CiscoInternalStorageCollectionAPI POST called')
        return 'POST is not a supported command for CiscoInternalStorageCollectionAPI', 405

    # HTTP PATCH
    def patch(self):
        logging.info('CiscoInternalStorageCollectionAPI PATCH called')
        return 'PATCH is not a supported command for CiscoInternalStorageCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('CiscoInternalStorageCollectionAPI DELETE called')
        return 'DELETE is not a supported command for CiscoInternalStorageCollectionAPI', 405



# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# LogEntry API File

"""
Collection API:  GET, POST
Singleton  API:  GET, POST
"""

import g

import sys, traceback
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource
from .Manager_api import members as manager_members
from .LogServices_api import members as logservices_members
from api_emulator.utils import update_nested_dict

members = {}

INTERNAL_ERROR = 500


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
            # Find the entry with the correct value for Id
            resp = 404
            if ident in members:
                if ident1 in members[ident]:
                    if ident2 in members[ident][ident1]:
                        resp = members[ident][ident1][ident2], 200
                    else:
                        resp = f"LogEntry {ident2} for  LogServices {ident1} of Manager {ident} not found", 404
                else:
                    resp = f"LogServices {ident1} of Manager {ident} not found", 404  
            else:
                resp = f"Manager {ident} not found", 404          
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1 , ident2):
        logging.info('LogEntryAPI PUT called')
        return 'PUT is not a supported command for LogEntryAPI', 405

    # HTTP POST
    def post(self, ident, ident1, ident2):
        logging.info('LogEntryAPI POST called')
        try:
            if ident in manager_members:
                members.setdefault(ident, {})
                if ident1 in logservices_members[ident]:
                 members[ident].setdefault(ident1, {})
                else:
                    return "LogServices {} does not exist in Manager {}".format(ident1,ident), 404
            else:    
                return "Manager {} does not exist".format(ident), 404

            if ident2 in members[ident][ident1]:
                return "LogEntry {} already exists".format(ident2), 409
            else:
                members[ident][ident1][ident2] = request.json
                resp = members[ident][ident1][ident2], 200

        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1, ident2):
        logging.info('LogEntryAPI PATCH called')
        raw_dict = request.get_json(force=True)
        logging.info(f"Payload = {raw_dict}")
        try:
            if ident in manager_members:
                members.setdefault(ident, {})
                if ident1 in logservices_members[ident]:
                 members[ident].setdefault(ident1, {})
                else:
                    return "LogServices {} does not exist in Manager {}".format(ident1,ident), 404
            else:
                return "Manager {} does not exist".format(ident), 404

            # Update specific portions of the identified object
            update_nested_dict(members[ident][ident1][ident2], raw_dict)
            resp = members[ident][ident1][ident2], 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident, ident1):
        logging.info('LogEntryAPI DELETE called')
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


# LogEntry Collection API
class LogEntryCollectionAPI(Resource):

    def __init__(self):
        logging.info('LogEntryCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.id': " ",
            '@odata.type': '#LogEntryCollection.LogEntryCollection',
            '@odata.context': self.rb + '$metadata#LogEntryCollection.LogEntryCollection',
            'Name': 'Ethernet Interfaces Collection',
            "Members": [],
            "Members@odata.count": 0,
        }

    # HTTP GET
    def get(self,ident,ident1):
        logging.info('LogEntryCollectionAPI GET called')
        try:
            self.config["@odata.id"] = "/redfish/v1/Managers/<string:ident>/LogServices/<string:ident1>/Entries".format(ident)
            self.config["Members"] = [{'@odata.id': LogEntry['@odata.id']} for LogEntry in list(members.get(ident, {}).get(ident1, {}).values())]
            self.config["Members@odata.count"] = len(members[ident].setdefault(ident1, {}))
            resp = self.config, 200
            
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
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



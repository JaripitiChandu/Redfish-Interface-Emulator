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
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource
from .Manager_api import members as manager_members
from .cisco_internal_storage_api import members as internalstorage_members
from .ciscopartition_api import members as partition_members
members = {}

INTERNAL_ERROR = 500


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
            if ident in members:
                if ident1 in members[ident]:
                    if ident2 in members[ident][ident1]:
                        resp = members[ident][ident1][ident2], 200
                    else:
                        resp = f"CiscoFile {ident2} for  CiscoPartition {ident1} of Manager {ident} not found", 404
                else:
                    resp = f"CiscoPartition {ident1} of Manager {ident} not found", 404  
            else:
                resp = f"Manager {ident} not found", 404          
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1 , ident2):
        logging.info('CiscoFileAPI PUT called')
        return 'PUT is not a supported command for CiscoFileAPI', 405

    # HTTP POST
    def post(self, ident, ident1, ident2):
        logging.info('CiscoFileAPI POST called')
        try:
            if ident in manager_members:
                members.setdefault(ident, {})
                if "FlexMMC" not in internalstorage_members[ident]:
                    return "CiscoInternalStorage FlexMMC not found in Manager {}".format(ident), 404
                elif ident1 in partition_members.get(ident,{}):
                    members[ident].setdefault(ident1, {})
                else:
                    return "{} of CiscoInternalStorage FlexMMC not found in Manager {}".format(ident1,ident),404      
            else:
                return "Manager {} not found".format(ident), 404

            if ident2 in partition_members:
                return "CiscoFile {} already exists".format(ident2), 409
            else:
                members[ident][ident1][ident2] = request.json
                resp = members[ident][ident1][ident2], 200

        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1):
        logging.info('CiscoFileAPI PATCH called')
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
        logging.info('CiscoFileAPI DELETE called')
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


# CiscoFile Collection API
class CiscoFileCollectionAPI(Resource):

    def __init__(self):
        logging.info('CiscoFileCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.id': " ",
            '@odata.type': '#CiscoFileCollection.CiscoFileCollection',
            '@odata.context': self.rb + '$metadata#CiscoFileCollection.CiscoFileCollection',
            'Name': 'CiscoFile Collection',
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self,ident,ident1):
        logging.info('CiscoFileCollectionAPI GET called')
        try:
            self.config["@odata.id"] = "/redfish/v1/Managers/{}/Oem/CiscoInternalStorage/FlexMMC/CiscoPartition/{}/CiscoFile".format(ident,ident1)
            self.config["Members"] = [{'@odata.id': CiscoFile['@odata.id']} for CiscoFile in list(members.get(ident, {}).get(ident1, {}).values())]
            self.config["Members@odata.count"] = len(self.config["Members"])
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
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


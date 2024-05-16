# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# CiscoPartition API File

"""
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

members = {}

INTERNAL_ERROR = 500


# CiscoPartition Singleton API
class CiscoPartitionAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('CiscoPartitionAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident, ident1):
        logging.info('CiscoPartitionAPI GET called')
        try:
            resp = 404     
            if ident in manager_members:
                if "FlexMMC" in internalstorage_members[ident]:
                    resp = members[ident][ident1], 200
                else:
                    resp = f"CiscoInternalStorage FlexMMC for  Manager {ident} not found", 404
            else:
                resp = f"Manager {ident} not found", 404          
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1 , ident2):
        logging.info('CiscoPartitionAPI PUT called')
        return 'PUT is not a supported command for CiscoPartitionAPI', 405

    # HTTP POST
    def post(self, ident, ident1):
        logging.info('CiscoPartitionAPI POST called')
        try:
            if ident in manager_members:
                members.setdefault(ident,{})
                if "FlexMMC" not in internalstorage_members[ident]:
                    return "CiscoInternalStorage FlexMMC not found in Manager {}".format(ident), 404
            else:    
                return "Manager {} not found".format(ident), 404

            if ident1 in internalstorage_members:
               return "CiscoPartition {} already exists for CiscoInternalStorage FlexMMC in Manager {}".format(ident1,ident), 409
            members[ident][ident1] = request.json
            resp = members[ident][ident1], 200

        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1):
        logging.info('CiscoPartitionAPI PATCH called')
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
        logging.info('CiscoPartitionAPI DELETE called')
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


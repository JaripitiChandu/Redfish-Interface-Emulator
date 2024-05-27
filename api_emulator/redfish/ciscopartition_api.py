# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# CiscoPartition API File

"""
Singleton  API:  GET, POST
"""

import g

import sys, traceback
import logging, json
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource
#from .Manager_api import members as manager_members
#from .cisco_internal_storage_api import members as internalstorage_members

members = {}

INTERNAL_ERROR = 500

PRIMARY_BNAME = b'managers'
BNAME = b'cisco_internal_storage'
OEM_BNAME = b'FlexMMC'  #OEM Resource
OEM_SR_BNAME = b'cisco_partition'   #OEM  Sub Resource
INDEX = b'value'

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
            with g.db.view() as tx:
                if not tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()):
                    resp = f"Manager {ident} not found", 404
                else:
                    b = tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()).bucket(BNAME).bucket(OEM_BNAME).bucket(OEM_SR_BNAME)
                    if b:
                        ident_bucket = b.bucket(str(ident1).encode())
                        if not ident_bucket:
                            resp = f"CiscoPartition {ident1} for {OEM_BNAME} Manager {ident} not found", 404
                        else:
                            value = ident_bucket.get(INDEX).decode()
                            resp = json.loads(value), 200
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
            with g.db.update() as tx:
                managers = tx.bucket(PRIMARY_BNAME)
                if managers:
                    managers_ident = managers.bucket(str(ident).encode())
                    if managers_ident:
                        oem_storage=managers_ident.bucket(BNAME).bucket(OEM_BNAME)
                    else:
                        resp = f"Manager {ident} {BNAME} {OEM_BNAME} not found", 404
                else:
                    resp = f"Manager {ident} not found", 404

                oem_partition=oem_storage.bucket(OEM_SR_BNAME)

                if not oem_partition:
                    oem_partition = oem_storage.create_bucket(OEM_SR_BNAME)

                oem_partition_ident = oem_partition.bucket(str(ident1).encode())

                if oem_partition_ident:
                    resp = f"CiscoPartition {ident1} for {str(OEM_BNAME)} already exists in Manager {ident}", 409
                else:
                    ident_bucket = oem_partition.create_bucket(str(ident1).encode())
                    ident_bucket.put(INDEX, json.dumps(request.json).encode())
                    resp = request.json, 200

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


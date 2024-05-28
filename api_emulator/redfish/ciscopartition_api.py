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

from g import INDEX, INTERNAL_SERVER_ERROR

PRIMARY_BNAME = b'Managers'
BNAME = b'CiscoInternalStorage'
OEM_BNAME = b'FlexMMC'  #OEM Resource
OEM_SR_BNAME = b'CiscoPartition'   #OEM  Sub Resource

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
                            resp = f"CiscoPartition {ident1} for {OEM_BNAME.decode('utf-8')} Manager {ident} not found", 404
                        else:
                            value = ident_bucket.get(INDEX).decode()
                            resp = json.loads(value), 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
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
                        oem_storage = managers_ident.bucket(BNAME).bucket(OEM_BNAME)
                        if oem_storage:
                                oem_partition=oem_storage.bucket(OEM_SR_BNAME)
                        else:
                            return f"{OEM_BNAME.decode('utf-8')} of CiscoInternalStorage for Manager {ident} not found", 404
                    else:
                        return f"{OEM_BNAME.decode('utf-8')} of CiscoInternalStorage for Manager {ident} not found", 404
                else:
                    return f"Manager {ident} not found", 404

                if not oem_partition:
                    oem_partition = oem_storage.create_bucket(OEM_SR_BNAME)

                oem_partition_ident = oem_partition.bucket(str(ident1).encode())

                if oem_partition_ident:
                    return f"CiscoPartition {ident1} for {OEM_BNAME.decode('utf-8')} already exists in Manager {ident}", 409
                else:
                    ident_bucket = oem_partition.create_bucket(str(ident1).encode())
                    ident_bucket.put(INDEX, json.dumps(request.json).encode())
                    resp = request.json, 201

        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1):
        logging.info('CiscoPartitionAPI PATCH called')
        return 'PATCH is not a supported command for CiscoPartitionAPI', 405


    # HTTP DELETE
    def delete(self, ident, ident1):
        logging.info('CiscoPartitionAPI DELETE called')
        return 'DELETE is not a supported command for CiscoPartitionAPI', 405


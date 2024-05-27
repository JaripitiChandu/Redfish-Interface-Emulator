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
from .Manager_api import members as manager_members
from .cisco_internal_storage_api import members as internalstorage_members
from .ciscopartition_api import members as partition_members

members = {}

PRIMARY_BNAME = b'managers'
BNAME = b'cisco_internal_storage'
OEM_BNAME = b'FlexMMC'  #OEM Resource
OEM_SR_BNAME = b'cisco_partition'   #OEM  Sub Resource
OEM_SR_BNAME_2 = b'cisco_files'
INDEX = b'value'

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
            resp = 404
            with g.db.view() as tx:
                if not tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()):
                    resp = f"Manager {ident} not found", 404
                else:
                    b = tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()).bucket(BNAME).bucket(OEM_BNAME).bucket(OEM_SR_BNAME).bucket(str(ident1).encode()).bucket(OEM_SR_BNAME_2)
                    if b:
                        ident_bucket = b.bucket(str(ident2).encode())
                        if not ident_bucket:
                            resp = f"CiscoFile {ident2} of CiscoPartition {ident1} for {OEM_BNAME} Manager {ident} not found", 404
                        else:
                            value = ident_bucket.get(INDEX).decode()
                            resp = json.loads(value), 200
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
            with g.db.update() as tx:
                managers = tx.bucket(PRIMARY_BNAME)
                if managers:
                    managers_ident = managers.bucket(str(ident).encode())
                    if managers_ident:
                        oem_storage = managers_ident.bucket(BNAME).bucket(OEM_BNAME)
                        if oem_storage:
                            oem_partition_ident = oem_storage.bucket(OEM_SR_BNAME).bucket(str(ident1).encode())
                            if oem_partition_ident:
                                oem_file=oem_partition_ident.bucket(OEM_SR_BNAME_2)
                            else:
                                resp = f"CiscoPartition {ident1} for {str(OEM_BNAME)} not found in Manager {ident}", 404
                        else:
                            resp = f"Manager {ident} {BNAME} {OEM_BNAME} not found", 404
                    else:
                        resp = f"Manager {ident} not found", 404

                if not oem_file:
                    oem_file = oem_partition_ident.create_bucket(OEM_SR_BNAME_2)

                oem_file_ident = oem_file.bucket(str(ident2).encode())

                if oem_file_ident:
                    resp = f"CiscoFile {ident2} of CiscoPartition {ident1} for {str(OEM_BNAME)} already exists in Manager {ident}", 409
                else:
                    ident_bucket = oem_file.create_bucket(str(ident2).encode())
                    ident_bucket.put(INDEX, json.dumps(request.json).encode())
                    resp = request.json, 200

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
            bucket_members = []
            with g.db.view() as tx:
                b = tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()).bucket(BNAME).bucket(OEM_BNAME).bucket(OEM_SR_BNAME).bucket(str(ident1).encode()).bucket(OEM_SR_BNAME_2)

                if not b:
                    resp = f"CiscoFile of CiscoPartition {ident1} for {str(OEM_BNAME)} not found in Manager {ident}", 404
                else:
                    for k, v in b:
                        if not v:
                            if b.bucket(k):
                                bucket_members.append(json.loads(b.bucket(k).get(INDEX).decode())['@odata.id'])
            self.config["@odata.id"] = "/redfish/v1/Managers/{}/Oem/CiscoInternalStorage/FlexMMC/CiscoPartition/{}/CiscoFile".format(ident,ident1)
            self.config['Members'] = [{'@odata.id': x} for x in bucket_members]
            self.config["Members@odata.count"] = len(bucket_members)
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


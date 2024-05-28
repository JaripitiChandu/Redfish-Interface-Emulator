# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# EthernetInterface API File

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

from g import INDEX, INTERNAL_SERVER_ERROR

PRIMARY_BNAME = b'Managers'
BNAME = b'EthernetInterfaces'

# EthernetInterface Singleton API
class EthernetInterfaceAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('EthernetInterfaceAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident, ident1):
        logging.info('EthernetInterfaceAPI GET called')
        try:
            # Find the entry with the correct value for Id
            resp = 404
            with g.db.view() as tx:
                if not tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()):
                    resp = f"Manager {ident} not found", 404
                else:
                    b = tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()).bucket(BNAME)
                    if b:
                        ident_bucket = b.bucket(str(ident1).encode())
                        if not ident_bucket:
                            resp = f" Etherent Interface {ident1} for Manager {ident} not found", 404
                        else:
                            value = ident_bucket.get(INDEX).decode()
                            resp = json.loads(value), 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1):
        logging.info('EthernetInterfaceAPI PUT called')
        return 'PUT is not a supported command for EthernetInterfaceAPI', 405

    # HTTP POST
    def post(self, ident, ident1):
        logging.info('EthernetInterfaceAPI POST called')
        try:
            with g.db.update() as tx:
                managers = tx.bucket(PRIMARY_BNAME)
                if managers:
                    managers_ident = managers.bucket(str(ident).encode())
                    if managers_ident:
                        eth_interfaces = managers_ident.bucket(BNAME)
                else:
                    return f"Manager {ident} not found", 404

                if not eth_interfaces:
                    eth_interfaces = managers_ident.create_bucket(BNAME)

                eth_interfaces_ident = eth_interfaces.bucket(str(ident1).encode())

                if eth_interfaces_ident:
                    return f"Ethernet Interfaces {ident1} already exists in Manager {ident}", 409
                else:
                    ident_bucket = eth_interfaces.create_bucket(str(ident1).encode())
                    ident_bucket.put(INDEX, json.dumps(request.json).encode())
                    resp = request.json, 201

        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1):
        logging.info('EthernetInterfaceAPI PATCH called')
        return 'PATCH is not a supported command for EthernetInterfaceAPI', 405


    # HTTP DELETE
    def delete(self, ident, ident1):
        logging.info('EthernetInterfaceAPI DELETE called')
        return 'DELETE is not a supported command for EthernetInterfaceAPI', 405

# EthernetInterface Collection API
class EthernetInterfaceCollectionAPI(Resource):

    def __init__(self):
        logging.info('EthernetInterfaceCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.id': " ",
            '@odata.type': '#EthernetInterfaceCollection.EthernetInterfaceCollection',
            '@odata.context': self.rb + '$metadata#EthernetInterfaceCollection.EthernetInterfaceCollection',
            'Name': 'Ethernet Interfaces Collection',
            "Members": [],
            "Members@odata.count": 0,
            "Description": "Collection of EthernetInterfaces for this Manager"
        }

    # HTTP GET
    def get(self,ident):
        logging.info('EthernetInterfaceCollectionAPI GET called')
        try:
            bucket_members = []
            with g.db.view() as tx:
                b = tx.bucket(PRIMARY_BNAME).bucket(str(ident).encode()).bucket(BNAME)

                if not b:
                    resp = f'Ethernet Interfaces for Managers {ident} not found', 404
                else:
                    for k, v in b:
                        if not v:
                            if b.bucket(k):
                                bucket_members.append(json.loads(b.bucket(k).get(INDEX).decode())['@odata.id'])
            self.config["@odata.id"] = "/redfish/v1/Manager/{}/EthernetInterfaces".format(ident)
            self.config['Members'] = [{'@odata.id': x} for x in bucket_members]
            self.config["Members@odata.count"] = len(bucket_members)
            resp = self.config, 200
            
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self,ident):
        logging.info('EthernetInterfaceCollectionAPI PUT called')
        return 'PUT is not a supported command for EthernetInterfaceCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self,ident):
        logging.info('EthernetInterfaceCollectionAPI POST called')
        return 'POST is not a supported command for EthernetInterfaceCollectionAPI', 405

    # HTTP PATCH
    def patch(self):
        logging.info('EthernetInterfaceCollectionAPI PATCH called')
        return 'PATCH is not a supported command for EthernetInterfaceCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('EthernetInterfaceCollectionAPI DELETE called')
        return 'DELETE is not a supported command for EthernetInterfaceCollectionAPI', 405



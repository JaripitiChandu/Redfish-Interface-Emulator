# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Chassis API File

"""
Collection API:  GET, POST
Singleton  API:  GET, POST, PATCH, DELETE
"""

import g
from g import db, INDEX, INTERNAL_SERVER_ERROR

import sys, traceback, json
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

members = {}
BNAME = b"Fabrics"

INTERNAL_ERROR = 500


# Fabrics Singleton API
class Fabric(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.

    def __init__(self, **kwargs):
        logging.info(f'{self.__class__.__name__} init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info(self.__class__.__name__ +' GET called')
        try:
            # Find the entry with the correct value for Id
            with db.view() as tx:
                b = tx.bucket(BNAME)
                if not b:
                    return "Fabric " + ident + " not found" , 404
                fabric = b.bucket(str(ident).encode())
                if not fabric:
                    resp = "Fabric " + ident + " not found" , 404
                else:
                    resp = json.loads(fabric.get(INDEX).decode()), 200
        except Exception:
            traceback.print_exc()
            resp = "Internal Server Error", INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info(self.__class__.__name__ + ' PUT called')
        return 'PUT is not a supported command for ChassisAPI', 405

    # HTTP POST
    # This is an emulator-only POST command that creates new resource
    # instances from a predefined template. The new instance is given
    # the identifier "ident", which is taken from the end of the URL.
    # PATCH commands can then be used to update the new instance.
    def post(self, ident):
        logging.info(self.__class__.__name__ + ' POST called')
        try:
            with db.update() as tx:
                b = tx.bucket(BNAME)
                if not b:
                    b = tx.create_bucket(BNAME)
                system = b.create_bucket(str(ident).encode())
                system.put(INDEX, json.dumps(request.json).encode())
            resp = request.json, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident):
        logging.info(self.__class__.__name__ + ' PATCH called')
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
        logging.info(self.__class__.__name__ + ' DELETEs called')
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


# Fabrics Collection API
class Fabrics(Resource):

    def __init__(self):
        logging.info(f'{self.__class__.__name__} init called')
        self.rb = g.rest_base
        bucket_members = []

        with db.view() as tx:
            b = tx.bucket(BNAME)
            if b:
                for k, v in b:
                    if not v:
                        if b.bucket(k):
                            bucket_members.append(json.loads(b.bucket(k).get(INDEX).decode())['@odata.id'])
        self.config = {
            "@odata.id": self.rb + "Fabrics",
            "@odata.type": "#FabricCollection.FabricCollection",
            "@odata.context": self.rb + "$metadata#FabricCollection.FabricCollection",
            "Description": "Collection of Fabrics",
            "Name": "Fabric Collection",
            "Members@odata.count": len(bucket_members),
            "Members":  [{'@odata.id': x} for x in bucket_members],
        }

    # HTTP GET
    def get(self):
        logging.info(self.__class__.__name__ +' GET called')
        try:
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info(self.__class__.__name__ + ' PUT called')
        return 'PUT is not a supported command for ChassisCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self):
        logging.info(self.__class__.__name__ + ' PATCH called')
        try:
            config = request.get_json(force=True)
            ok, msg = self.verify(config)
            if ok:
                members[config['Id']] = config
                resp = config, 201
            else:
                resp = msg, 400
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self):
        logging.info('ChassisCollectionAPI PATCH called')
        return 'PATCH is not a supported command for ChassisCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('ChassisCollectionAPI DELETE called')
        return 'DELETE is not a supported command for ChassisCollectionAPI', 405
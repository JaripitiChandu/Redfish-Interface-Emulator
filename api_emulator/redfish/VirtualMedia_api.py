# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# ComputerSystem API File

"""
Collection API:  GET, POST
Singleton  API:  GET, POST, PATCH, DELETE
"""

import sys, traceback
import logging, json
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource
from api_emulator.utils import update_nested_dict

from g import db, INDEX, INTERNAL_SERVER_ERROR
from .Manager_api import BNAME as MGR_BNAME

members = {}
BNAME = b"VirtualMedia"

INTERNAL_ERROR = 500


# Storage Singleton API
class VirtualMediaAPI(Resource):

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
    def get(self, ident1, ident2):
        logging.info(self.__class__.__name__ +' GET called')
        try:
            with db.view() as tx:
                sb = tx.bucket(MGR_BNAME)
                if sb:
                    system = sb.bucket(str(ident1).encode())
                    if system:
                        mems = system.bucket(BNAME)
                        if mems:
                            mem = mems.bucket(str(ident2).encode())
                            if mem:
                                resp = json.loads(mem.get(INDEX).decode()), 200
                            else:
                                return f"VirtualMedia {ident2} not found in Manager {ident1}", 404
                        else:
                            return f"VirtualMedia {ident2} not found in Manager {ident1}", 404
                    else:
                        return "Manager " + ident1 + " not found" , 404
                else:
                    return "Manager " + ident1 + " not found" , 404
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info(self.__class__.__name__ + ' PUT called')
        return f'PUT is not a supported command for {self.__class__.__name__}', 405

    # HTTP POST
    # This is an emulator-only POST command that creates new resource
    # instances from a predefined template. The new instance is given
    # the identifier "ident", which is taken from the end of the URL.
    # PATCH commands can then be used to update the new instance.
    def post(self, ident1: str, ident2: int):
        logging.info(self.__class__.__name__ + ' POST called')
        try:
            with db.update() as tx:
                b = tx.bucket(MGR_BNAME)
                if b:
                    sb = b.bucket(str(ident1).encode())
                    if sb:
                        mems = sb.bucket(BNAME)
                        if not mems:
                            mems = sb.create_bucket(BNAME)
                        if mems.bucket(str(ident2).encode()):
                            return f"VirtualMedia {ident2} is already present in Manager {ident1}", 409
                        else:
                            mem = mems.create_bucket(str(ident2).encode())
                            mem.put(INDEX, json.dumps(request.json).encode())
                    else:
                        return f"Manager {ident1} does not exist", 404
                else:
                    return f"Manager {ident1} does not exist", 404
            resp = request.json, 201
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident1):
        logging.info(self.__class__.__name__ + ' PATCH called')
        raw_dict = request.get_json(force=True)
        try:
            # Update specific portions of the identified object
            update_nested_dict(members[ident1], raw_dict)
            resp = members[ident1], 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP DELETE
    def delete(self, ident):
        logging.info(self.__class__.__name__ + ' DELETE called')
        try:
            if ident in members:
                del(members[ident])
                resp = 200
            else:
                resp = "Storage" + ident + " not found", 404
        except Exception:
            traceback.print_exc()
            resp = "Internal Server Error", INTERNAL_ERROR
        return resp

# VirtualMedia Collection API
class VirtualMediaCollectionAPI(Resource):

    def __init__(self):
        logging.info(self.__class__.__name__ + ' init called')
        self.config = {
            "@odata.id": "",
            "@odata.type": "#VirtualMediaCollection.VirtualMediaCollection",
            "@odata.context": "/redfish/v1/$metadata#VirtualMediaCollection.VirtualMediaCollection",
            "Description": "Redfish-BMC Virtual Media Service Settings",
            "Name": "Virtual Media Services",
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self, ident):
        logging.info(self.__class__.__name__ +' GET called')
        try:
            bucket_members = []

            with db.view() as tx:
                systems = tx.bucket(MGR_BNAME)
                if systems:
                    sb = systems.bucket(str(ident).encode())
                    if sb:
                        mems = sb.bucket(BNAME)
                        if mems:
                            for k, v in mems:
                                if not v and mems.bucket(k):
                                    bucket_members.append(json.loads(mems.bucket(k).get(INDEX).decode())['@odata.id'])

            self.config["@odata.id"] = "/redfish/v1/Managers/{}/VirtualMedia".format(ident)
            self.config["Members"] = [{'@odata.id': x} for x in bucket_members]
            self.config["Members@odata.count"] = len(bucket_members)
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info(self.__class__.__name__ + ' PUT called')
        return f'PUT is not a supported command for {self.__class__.__name__}', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    # POST should allow adding multiple instances to a collection.
    # For now, this only adds one instance.
    # TODO: 'id' should be obtained from the request data.
    def post(self, ident):
        logging.info(self.__class__.__name__ + ' POST called')
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
    def patch(self, ident):
        logging.info(self.__class__.__name__ + ' PATCH called')
        return f'PATCH is not a supported command for {self.__class__.__name__}', 405

    # HTTP DELETE
    def delete(self, ident):
        logging.info(self.__class__.__name__ + ' DELETE called')
        return f'DELETE is not a supported command for {self.__class__.__name__}', 405
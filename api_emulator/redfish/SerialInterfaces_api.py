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
BNAME = b"SerialInterfaces"

INTERNAL_ERROR = 500


# SerialInterface Singleton API
class SerialInterface(Resource):

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
                b = tx.bucket(MGR_BNAME)
                if b:
                    mb = b.bucket(str(ident1).encode())
                    if mb:
                        sb = mb.bucket(BNAME)
                        if sb:
                            sib = sb.bucket(str(ident2).encode())
                            if sib:
                                resp = json.loads(sib.get(INDEX).decode()), 200
                            else:
                                return f"SerialInterface {ident2} not found in Manager {ident1}", 404
                        else:
                            return f"SerialInterface {ident2} not found in Manager {ident1}", 404
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
                    mb = b.bucket(str(ident1).encode())
                    if mb:
                        sb = mb.bucket(BNAME)
                        if not sb:
                            sb = mb.create_bucket(BNAME)
                        if sb.bucket(str(ident2).encode()):
                            return f"SerialInterface {ident2} is already present in Manager {ident1}", 409
                        else:
                            sib = sb.create_bucket(str(ident2).encode())
                            sib.put(INDEX, json.dumps(request.json).encode())
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
    def patch(self, ident1, ident2):
        logging.info(self.__class__.__name__ + ' PATCH called')
        raw_dict = request.get_json(force=True)
        logging.info(f"payload = {json.dumps(raw_dict)}")
        try:
            with db.update() as tx:
                b = tx.bucket(MGR_BNAME)
                if b:
                    mb = b.bucket(str(ident1).encode())
                    if mb:
                        sb = mb.bucket(BNAME)
                        if sb:
                            sib = sb.bucket(str(ident2).encode())
                            if sib:
                                config = json.loads(sib.get(INDEX).decode())
                                update_nested_dict(config, raw_dict)
                                sib.put(INDEX, json.dumps(config).encode())
                            else:
                                return f"SerialInterface {ident2} not found in Manager {ident1}", 404
                        else:
                            return f"SerialInterface {ident2} not found in Manager {ident1}", 404
                    else:
                        return f"Manager {ident1} does not exist", 404
                else:
                    return f"Manager {ident1} does not exist", 404
            resp = config, 200
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
                resp = "Manager" + ident + " not found", 404
        except Exception:
            traceback.print_exc()
            resp = "Internal Server Error", INTERNAL_ERROR
        return resp

# SerialInterface Collection API
class SerialInterfaces(Resource):

    def __init__(self):
        logging.info(self.__class__.__name__ + ' init called')
        self.config = {
            "@odata.id": "",
            "@odata.type": "#SerialInterfaceCollection.SerialInterfaceCollection",
            "@odata.context": "/redfish/v1/$metadata#SerialInterfaceCollection.SerialInterfaceCollection",
            "Description": "Collection of Serial Interfaces for this System",
            "Name": "Serial Interface Collection",
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self, ident):
        logging.info(self.__class__.__name__ +' GET called')
        try:
            bucket_members = []

            with db.view() as tx:
                b = tx.bucket(MGR_BNAME)
                if b:
                    mb = b.bucket(str(ident).encode())
                    if mb:
                        sb = mb.bucket(BNAME)
                        if sb:
                            for k, v in sb:
                                if not v and sb.bucket(k):
                                    bucket_members.append(json.loads(sb.bucket(k).get(INDEX).decode())['@odata.id'])

            self.config["@odata.id"] = "/redfish/v1/Managers/{}/SerialInterfaces".format(ident)
            self.config["Members"] = [{'@odata.id': x} for x in bucket_members]
            self.config["Members@odata.count"] = len(bucket_members)
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
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
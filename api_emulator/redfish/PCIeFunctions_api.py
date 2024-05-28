# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# ComputerSystem API File

"""
Collection API:  GET, POST
Singleton  API:  GET, POST, PATCH, DELETE
"""

import sys, traceback
from pprint import pprint
import logging, json
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource
from .ComputerSystem_api import BNAME as SYS_BNAME
from .PCIeDevice_api import BNAME as DEV_BNAME
from .ResetActionInfo_api import ResetActionInfo_API
from .ResetAction_api import ResetAction_API

from g import db, INDEX, INTERNAL_SERVER_ERROR

members = {}
BNAME = b"PCIeFunctions"

INTERNAL_ERROR = 500


# PCIeDevice Singleton API
class PCIeFunction(Resource):

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
    def get(self, ident1, ident2, ident3):
        logging.info(self.__class__.__name__ +' GET called')
        try:
            with db.view() as tx:
                sb = tx.bucket(SYS_BNAME)
                if sb:
                    system = sb.bucket(str(ident1).encode())
                    if system:
                        devices = system.bucket(DEV_BNAME)
                        if devices:
                            device = devices.bucket(str(ident2).encode())
                            if device:
                                funcs = device.bucket(BNAME)
                                if funcs:
                                    func = funcs.bucket(str(ident3).encode())
                                    if func:
                                        resp = json.loads(func.get(INDEX).decode()), 200
                                    else:
                                        return f"PCIeFunction {ident3} not found in PCIeDevice {ident2} of System {ident1}", 404
                                else:
                                    return f"PCIeFunction {ident3} not found in PCIeDevice {ident2} of System {ident1}", 404
                            else:
                                return f"PCIeDevice {ident2} not found in System {ident1}", 404
                        else:
                            return f"PCIeDevice {ident2} not found in System {ident1}", 404
                    else:
                        return "System " + ident1 + " not found" , 404
                else:
                    return "System " + ident1 + " not found" , 404
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
    def post(self, ident1, ident2, ident3):
        logging.info(self.__class__.__name__ + ' POST called')
        try:
            with db.update() as tx:
                b = tx.bucket(SYS_BNAME)
                if b:
                    sb = b.bucket(str(ident1).encode())
                    if sb:
                        devices = sb.bucket(DEV_BNAME)
                        if devices:
                            device = devices.bucket(str(ident2).encode())
                            if device:
                                funcs = device.bucket(BNAME)
                                if not funcs:
                                    funcs = device.create_bucket(BNAME)
                                if funcs.bucket(str(ident2).encode()):
                                    return f"PCIeFunction {ident3} is already present in PCIeDevice {ident2} of System {ident1}", 409
                                else:
                                    func = funcs.create_bucket(str(ident3).encode())
                                    func.put(INDEX, json.dumps(request.json).encode())
                            else:
                                return f"PCIeDevice {ident2} does not exist in System {ident1}", 404
                        else:
                            return f"PCIeDevice {ident2} does not exist in System {ident1}", 404
                    else:
                        return f"System {ident1} does not exist", 404
                else:
                    return f"System {ident1} does not exist", 404
            resp = request.json, 201
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
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
        logging.info(self.__class__.__name__ + ' DELETE called')
        try:
            if ident in members:
                del(members[ident])
                resp = 200
            else:
                resp = "PCIeDevice" + ident + " not found", 404
        except Exception:
            traceback.print_exc()
            resp = "Internal Server Error", INTERNAL_ERROR
        return resp

# PCIeDevice Collection API
class PCIeFunctions(Resource):

    def __init__(self):
        logging.info(self.__class__.__name__ + ' init called')
        self.config = {
            "@odata.id": '',
            "@odata.type": "#PCIeFunctionCollection.PCIeFunctionCollection",
            "@odata.context": "/redfish/v1/$metadata#PCIeFunctionCollection.PCIeFunctionCollection",
            "Description": "Collection of PCIeFunction resource instances for this PCIeDevice",
            "Name": "PCIeFunction Collection",
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self, ident1, ident2):
        logging.info(self.__class__.__name__ +' GET called')
        try:
            bucket_members = []

            with db.view() as tx:
                systems = tx.bucket(SYS_BNAME)
                if systems:
                    sb = systems.bucket(str(ident1).encode())
                    if sb:
                        devices = sb.bucket(DEV_BNAME)
                        if devices:
                            device = devices.bucket(str(ident2).encode())
                            if device:
                                b = device.bucket(BNAME)
                                if b:
                                    for k, v in b:
                                        if not v and b.bucket(k):
                                            bucket_members.append(json.loads(b.bucket(k).get(INDEX).decode())['@odata.id'])

            self.config["@odata.id"] = "/redfish/v1/Systems/{}/PCIeDevices/{}/PCIeFunctions".format(ident1, ident2)
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
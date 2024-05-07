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

from .ResetActionInfo_api import ResetActionInfo_API
from .ResetAction_api import ResetAction_API

members = {}

INTERNAL_ERROR = 500


# ComputerSystem Singleton API
class Processor(Resource):

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
            # Find the entry with the correct value for Id
            if ident1 in members:
                if ident2 in members[ident1]:
                    resp = members[ident1][ident2], 200
                else:
                    resp = f"Processor {ident2} for system {ident1} not found", 404
            else:
                resp = f"Processor {ident2} for system {ident1} not found", 404
        except Exception:
            traceback.print_exc()
            resp = "Internal Server Error", INTERNAL_ERROR
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
    def post(self, ident1, ident2):
        logging.info(self.__class__.__name__ + ' POST called')
        try:
            members.setdefault(ident1, {})
            if ident2 in members[ident1]:
                return ident2 + " processor already exists", 409
            else:
                members[ident1][ident2] = request.json
            resp = members[ident1][ident2], 200
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
        logging.info(self.__class__.__name__ + ' DELETE called')
        try:
            if ident in members:
                del(members[ident])
                resp = 200
            else:
                resp = "Processor" + ident + " not found", 404
        except Exception:
            traceback.print_exc()
            resp = "Internal Server Error", INTERNAL_ERROR
        return resp

# Chassis Collection API
class Processors(Resource):

    def __init__(self):
        logging.info('ChassisCollectionAPI init called')
        self.config = {
    "@odata.id": "",
    "@odata.type": "#ProcessorCollection.ProcessorCollection",
    "@odata.context": "/redfish/v1/$metadata#ProcessorCollection.ProcessorCollection",
    "Description": "Collection of Processors for this system",
    "Name": "Processors Collection",
    "Members": [],
    "Members@odata.count": 0
}
        
        # {
        #     '@odata.context': self.rb + '$metadata#ChassisCollection.ChassisCollection',
        #     '@odata.id': self.rb + 'Chassis',
        #     '@odata.type': '#ChassisCollection.1.0.0.ChassisCollection',
        #     'Name': 'Chassis Collection',
        #     'Members@odata.count': len(members),
        #     'Members': [{'@odata.id': x['@odata.id']} for
        #                 x in list(members.values())]
        # }

    # HTTP GET
    def get(self, ident):
        logging.info(self.__class__.__name__ +' GET called')
        try:
            self.config["@odata.id"] = "/redfish/v1/Systems/{}/Processors".format(ident)
            self.config["Members"] = [{'@odata.id': procs['@odata.id']} for procs in list(members.get(ident, {}).values())]
            self.config["Members@odata.count"] = len(members.setdefault(ident, {}))
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
# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# IMCImages API File

"""
Collection API:  GET
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


# IMCImages Singleton API
class IMCImagesAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.
    def __init__(self, **kwargs):
        logging.info('IMCImagesAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident, ident1, ident2):
        logging.info('IMCImagesAPI GET called')
        try:
            # Find the entry with the correct value for Id
            resp = 404
            # print("ident: ",ident)
            # print("ident1: ",members[ident])
            # print("ident1: ",members[ident][ident1])
            if ident in members:
                if ident1 in members[ident]:
                    if ident2 in members[ident][ident1]:
                        resp = members[ident][ident1][ident2], 200
                    else:
                        resp = f"NetworkDeviceFunction {ident2} for  NetworkAdapters {ident1} of Chassis {ident} not found", 404
                else:
                    resp = f"NetworkAdapters {ident1} of Chassis {ident} not found", 404  
            else:
                resp = f"Chassis {ident} not found", 404          
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident, ident1 , ident2):
        logging.info('IMCImagesAPI PUT called')
        return 'PUT is not a supported command for IMCImagesAPI', 405

    # HTTP POST
    # This is an emulator-only POST command that creates new resource
    # instances from a predefined template. The new instance is given
    # the identifier "ident", which is taken from the end of the URL.
    # PATCH commands can then be used to update the new instance.
    def post(self, ident, ident1, ident2):
        logging.info('IMCImagesAPI POST called')
        try:
            if ident in manager_members:
                members.setdefault(ident, {})
                if ident1 in internalstorage_members[ident]:
                 members[ident].setdefault(ident1, {})
                else:
                    return "CiscoInternalStorage {} not found in Manager {}".format(ident1,ident), 404
            else:    
                return "Manager {} not found".format(ident), 404

            if ident2 in members[ident][ident1]:
                return "IMCImage {} already exists".format(ident2), 409
            else:
                members[ident][ident1][ident2] = request.json
                resp = members[ident][ident1][ident2], 200

        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PATCH
    def patch(self, ident, ident1):
        logging.info('IMCImagesAPI PATCH called')
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
        logging.info('IMCImagesAPI DELETE called')
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


# IMCImages Collection API
class IMCImagesCollectionAPI(Resource):

    def __init__(self):
        logging.info('IMCImagesCollectionAPI init called')
        self.rb = g.rest_base
        self.config = {
            '@odata.id': " ",
            '@odata.type': '#IMCImagesCollection.IMCImagesCollection',
            '@odata.context': self.rb + '$metadata#IMCImagesCollection.IMCImagesCollection',
            'Name': 'IMCImages Collection',
            "Members": [],
            "Members@odata.count": 0
        }

    # HTTP GET
    def get(self,ident,ident1):
        logging.info('IMCImagesCollectionAPI GET called')
        try:
            self.config["@odata.id"] = "/redfish/v1/Managers/{}/Oem/CiscoInternalStorage/{}/CiscoPartition/IMCImages".format(ident,ident1)
            self.config["Members"] = [{'@odata.id': IMCImages['@odata.id']} for IMCImages in list(members.get(ident, {}).get(ident1, {}).values())]
            self.config["Members@odata.count"] = len(members[ident].setdefault(ident1, {}))
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_ERROR
        return resp

    # HTTP PUT
    def put(self,ident):
        logging.info('IMCImagesCollectionAPI PUT called')
        return 'PUT is not a supported command for IMCImagesCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    def post(self,ident):
        logging.info('IMCImagesCollectionAPI POST called')
        return 'POST is not a supported command for IMCImagesCollectionAPI', 405

    # HTTP PATCH
    def patch(self):
        logging.info('IMCImagesCollectionAPI PATCH called')
        return 'PATCH is not a supported command for IMCImagesCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('IMCImagesCollectionAPI DELETE called')
        return 'DELETE is not a supported command for IMCImagesCollectionAPI', 405


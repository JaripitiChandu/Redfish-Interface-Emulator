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
from .ComputerSystem_api import members as sys_members  
from .storage_api import members as storage_memebers
from .ResetActionInfo_api import ResetActionInfo_API
from .ResetAction_api import ResetAction_API

members = {}

INTERNAL_ERROR = 500


# Storage Singleton API
class DriveAPI(Resource):

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
            # Find the entry with the correct value for Id
            if ident1 in members:
                if ident2 in members[ident1]:
                    if ident3 in members[ident1][ident2]:
                        resp = members[ident1][ident2][ident3], 200
                    else:
                        resp = f"Drive {ident3} for storage {ident2} of system {ident1} not found", 404
                else:
                    resp = f"Storage {ident2} for system {ident1} not found", 404
            else:
                resp = f"Storage {ident2} for system {ident1} not found", 404
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
    def post(self, ident1, ident2, ident3):
        logging.info(self.__class__.__name__ + ' POST called')
        try:
            if ident1 in sys_members:
                members.setdefault(ident1, {})
            else:
                return f"System {ident1} not found", 404
            if ident2 in storage_memebers[ident1]:
                members[ident1].setdefault(ident2, {})
            else:
                print(storage_memebers)
                return f"Storage {ident2} not found for system {ident1}", 404
            
            if ident3 in members[ident1][ident2]:
                return "Resource already exists", 409
            else:
                members[ident1][ident2][ident3] = request.json
                resp = members[ident1][ident2][ident3], 200
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
                resp = "Storage" + ident + " not found", 404
        except Exception:
            traceback.print_exc()
            resp = "Internal Server Error", INTERNAL_ERROR
        return resp

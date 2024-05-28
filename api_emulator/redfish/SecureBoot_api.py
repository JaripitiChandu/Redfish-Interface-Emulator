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

from g import db, INDEX, INTERNAL_SERVER_ERROR
from .ComputerSystem_api import BNAME as SYS_BNAME

members = {}
BNAME = b"SecureBoot"

INTERNAL_ERROR = 500


# ComputerSystem Singleton API
class SecureBootAPI(Resource):

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
            with db.view() as tx:
                sb = tx.bucket(SYS_BNAME)
                if sb:
                    system = sb.bucket(str(ident).encode())
                    if system:
                        secure_boot = system.bucket(BNAME)
                        if secure_boot:
                            resp = json.loads(secure_boot.get(INDEX).decode()), 200
                        else:
                            return "SecureBoot for system " + ident + " not found" , 404
                    else:
                        return "System " + ident + " not found" , 404
                else:
                    return "System " + ident + " not found" , 404

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
    def post(self, ident):
        logging.info(self.__class__.__name__ + ' POST called')
        try:
            with db.update() as tx:
                b = tx.bucket(SYS_BNAME)
                if b:
                    sb = b.bucket(str(ident).encode())
                    if sb:
                        if sb.bucket(BNAME):
                            return f"SecureBoot is already present in System {ident}", 409
                        else:
                            secure_boot = sb.create_bucket(BNAME)
                            secure_boot.put(INDEX, json.dumps(request.json).encode())
                    else:
                        return f"System {ident} does not exist", 404
                else:
                    return f"System {ident} does not exist", 404
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
                resp = "Bios for system " + ident + " not found", 404
        except Exception:
            traceback.print_exc()
            resp = "Internal Server Error", INTERNAL_ERROR
        return resp


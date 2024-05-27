# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Singleton API: POST

import g
import requests
import os
import subprocess
import time

import sys, traceback, json
from flask import Flask, request, make_response, render_template, jsonify
from flask_restful import reqparse, Api, Resource
from subprocess import check_output

from g import db, INDEX, INTERNAL_SERVER_ERROR

#from .ComputerSystem_api import state_disabled, state_enabled

members={}
BNAME = b"Systems"
INTERNAL_ERROR = 500

class ResetAction_API(Resource):
    # kwargs is use to pass in the wildcards values to replace when the instance is created.
    def __init__(self, **kwargs):
        pass
    
    # HTTP POST
    def post(self,ident):
        try:
            with db.view() as tx:
                sb = tx.bucket(BNAME)
                if not sb:
                    return f"System {ident} not found!", 400
                if sb:
                    system = sb.bucket(str(ident).encode())
                    if not system:
                        return f"System {ident} not found!", 400
                    else:
                        resp = json.loads(system.get(INDEX).decode())
            try:
                json_payload = json.loads(request.data.decode("utf-8"))
                action = json_payload.get("ResetType")
                if action is None:
                    return "ResetType not provided in request payload", 400
            except Exception as e:
                return "Invalid or no JSON payload passed", 400
            allowableResetTypes = resp["Actions"]["#ComputerSystem.Reset"]["ResetType@Redfish.AllowableValues"]
            if action not in allowableResetTypes:
                return \
f"""Invalid reset type!
ResetType, possible values:
{allowableResetTypes}""", 400
            if action == "ForceOff":
                self.force_off(resp, ident)
            elif action == "On":
                self.force_on(resp, ident)
            elif action == "ForceRestart":
                self.force_off(resp, ident)
                self.force_on(resp, ident)
                print(f"System {ident} restarted")
            return 'POST Action request completed', 200
        except Exception as e:
            traceback.print_exc()
            return "Internal Server error", INTERNAL_ERROR

    @staticmethod
    def force_off(resp, ident):
        if resp["PowerState"] == "On":
            resp["PowerState"] = "resetting"
            resp['Status']['State'] = "resetting"
            with db.update() as tx:
                system = tx.bucket(BNAME).bucket(str(ident).encode())
                system.put(INDEX, json.dumps(resp).encode())
            time.sleep(10)
            resp["PowerState"] = "Off"
            resp['Status']['State'] = "Disabled"
            with db.update() as tx:
                system = tx.bucket(BNAME).bucket(str(ident).encode())
                system.put(INDEX, json.dumps(resp).encode())
            print (f'System {ident} Powered Off')
        else:
            print(f"System {ident} is already Powered Off")

    @staticmethod
    def force_on(resp, ident):
        if resp["PowerState"] == "Off":
            resp["PowerState"] = "resetting"
            resp['Status']['State'] = "resetting"
            with db.update() as tx:
                system = tx.bucket(BNAME).bucket(str(ident).encode())
                system.put(INDEX, json.dumps(resp).encode())
            time.sleep(10)
            resp["PowerState"] = "On"
            resp['Status']['State'] = "Enabled"
            with db.update() as tx:
                system = tx.bucket(BNAME).bucket(str(ident).encode())
                system.put(INDEX, json.dumps(resp).encode())
            print (f'System {ident} Powered On')
        else:
            print(f"System {ident} is already Powered On")

    # HTTP GET
    def get(self,ident):
        print ('ResetAction')
        print (members)
        return 'GET is not supported', 405, {'Allow': 'POST'}

    # HTTP PATCH
    def patch(self,ident):
         return 'PATCH is not supported', 405, {'Allow': 'POST'}

    # HTTP PUT
    def put(self,ident):
         return 'PUT is not supported', 405, {'Allow': 'POST'}

    # HTTP DELETE
    def delete(self,ident):
         return 'DELETE is not supported', 405, {'Allow': 'POST'}

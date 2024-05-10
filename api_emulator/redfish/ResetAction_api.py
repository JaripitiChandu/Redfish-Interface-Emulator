# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Singleton API: POST

import g
import requests
import os
import subprocess
import time

import sys, traceback
from flask import Flask, request, make_response, render_template, jsonify
from flask_restful import reqparse, Api, Resource
from subprocess import check_output

#from .ComputerSystem_api import state_disabled, state_enabled

members={}
INTERNAL_ERROR = 500

class ResetAction_API(Resource):
    # kwargs is use to pass in the wildcards values to replace when the instance is created.
    def __init__(self, **kwargs):
        pass
    
    # HTTP POST
    def post(self,ident):
        from .ComputerSystem_api import members as sys_members
        try:
            if ident not in sys_members:
                return f"System {ident} not found!", 400
            try:
                action = request.json.get("ResetType")
                if action is None:
                    return "ResetType not provided in request payload", 400
            except Exception as e:
                return "Invalid or no JSON payload passed", 400
            allowableResetTypes = sys_members[ident]["Actions"]["#ComputerSystem.Reset"]["ResetType@Redfish.AllowableValues"]
            if action not in allowableResetTypes:
                return f"""Invalid reset type!
ResetType, possible values:
{allowableResetTypes}""", 400
            if action == "ForceOff":
                self.force_off(sys_members, ident)
            elif action == "On":
                self.force_on(sys_members, ident)
            elif action == "ForceRestart":
                self.force_off(sys_members, ident)
                self.force_on(sys_members, ident)
                print(f"System {ident} restarted")
            return 'POST Action request completed', 200
        except Exception as e:
            traceback.print_exc()
            return "Internal Server error", INTERNAL_ERROR

    @staticmethod
    def force_off(sys_members, ident):
        if sys_members[ident]["PowerState"] == "On":
            sys_members[ident]["PowerState"] = "resetting"
            sys_members[ident]['Status']['State'] = "resetting"
            time.sleep(10)
            sys_members[ident]["PowerState"] = "Off"
            sys_members[ident]['Status']['State'] = "Disabled"
            print (f'System {ident} Powered Off')
        else:
            print(f"System {ident} is already Powered Off")

    @staticmethod
    def force_on(sys_members, ident):
        if sys_members[ident]["PowerState"] == "Off":
            sys_members[ident]["PowerState"] = "resetting"
            sys_members[ident]['Status']['State'] = "resetting"
            time.sleep(10)
            sys_members[ident]["PowerState"] = "On"
            sys_members[ident]['Status']['State'] = "Enabled"
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

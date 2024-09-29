# Copyright Notice:
# Copyright 2017-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# JsonSchemas API File

"""
Collection API:  GET
Singleton  API:  GET, POST
"""

import g

import sys, traceback, json
import logging
import copy
from flask import Flask, request, make_response, render_template
from flask_restful import reqparse, Api, Resource

from g import INTERNAL_SERVER_ERROR

INDICES = [1]

# JsonSchemas Singleton API
class JsonSchemasAPI(Resource):

    # kwargs is used to pass in the wildcards values to be replaced
    # when an instance is created via get_<resource>_instance().
    #
    # The call to attach the API establishes the contents of kwargs.
    # All subsequent HTTP calls go through __init__.
    #
    # __init__ stores kwargs in wildcards, which is used to pass
    # values to the get_<resource>_instance() call.


    def __init__(self, **kwargs):
        logging.info('JsonSchemasAPI init called')
        try:
            global wildcards
            wildcards = kwargs
        except Exception:
            traceback.print_exc()

    # HTTP GET
    def get(self, ident):
        logging.info('JsonSchemasAPI GET called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.get_value_from_bucket_hierarchy(bucket_hierarchy, INDICES)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self, ident):
        logging.info('JsonSchemasAPI PUT called')
        return 'PUT is not a supported command for JsonSchemasAPI', 405

    # HTTP POST
    def post(self, ident):
        logging.info('JsonSchemasAPI POST called')
        try:
            bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
            resp = g.post_value_to_bucket_hierarchy(bucket_hierarchy, INDICES, request.json)
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp


    # HTTP PATCH
    def patch(self, ident):
        logging.info('JsonSchemasAPI PATCH called')
        return 'PATCH is not a supported command for JsonSchemasAPI', 405

    # HTTP DELETE
    def delete(self, ident):
        logging.info('JsonSchemasAPI DELETE called')
        return 'DELETE is not a supported command for JsonSchemasAPI', 405



# JsonSchemas Collection API
class JsonSchemasCollectionAPI(Resource):

    def __init__(self):
        logging.info('JsonSchemasCollectionAPI init called')
        self.rb = g.rest_base
        bucket_hierarchy = request.path.lstrip(g.rest_base).split('/')
        passed, output = g.get_collection_from_bucket_hierarchy(bucket_hierarchy, INDICES[:-1])
        if not passed:
            return output, 404
        self.config = {
    "@odata.id": "/redfish/v1/JsonSchemas",
    "@odata.type": "#JsonSchemaFileCollection.JsonSchemaFileCollection",
    "@odata.context": "/redfish/v1/$metadata#JsonSchemaFileCollection.JsonSchemaFileCollection",
    "Description": "Schema Repository",
    "Name": "JSON Schema Collection",
    "Members": [
        {
            "@odata.id": "/redfish/v1/JsonSchemas/AccountService"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/AccountService.v1_7_2"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Assembly"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Assembly.v1_5_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Certificate"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Certificate.v1_3_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/CertificateCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/CertificateLocations"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/CertificateLocations.v1_0_2"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/CertificateService"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/CertificateService.v1_0_3"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Chassis"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Chassis.v1_14_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/ChassisCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/ComputerSystem"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/ComputerSystem.v1_15_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/ComputerSystemCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Drive"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Drive.v1_9_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/DriveCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/EthernetInterface"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/EthernetInterface.v1_6_2"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/EthernetInterfaceCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/EventDestination"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/EventDestination.v1_9_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/EventDestinationCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/EventService"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/EventService.v1_7_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/IPAddresses"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/IPAddresses.v1_1_3"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/JsonSchemaFile"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/JsonSchemaFile.v1_1_4"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/JsonSchemaFileCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/LogEntry"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/LogEntry.v1_8_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/LogEntryCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/LogService"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/LogService.v1_2_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/LogServiceCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Manager"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Manager.v1_12_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/ManagerAccount"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/ManagerAccount.v1_7_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/ManagerAccountCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/ManagerCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/ManagerNetworkProtocol"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/ManagerNetworkProtocol.v1_6_1"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Memory"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Memory.v1_12_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/MemoryCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Message"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Message.v1_1_1"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/MessageRegistry"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/MessageRegistry.v1_3_1"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/MessageRegistryCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/MessageRegistryFile"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/MessageRegistryFile.v1_1_3"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/MessageRegistryFileCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/NetworkAdapter"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/NetworkAdapter.v1_7_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/NetworkAdapterCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/NetworkDeviceFunction"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/NetworkDeviceFunction.v1_9_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/NetworkDeviceFunctionCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/NetworkInterface"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/NetworkInterface.v1_2_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/NetworkInterfaceCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/PCIeDevice"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/PCIeDevice.v1_7_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/PCIeDeviceCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/PCIeFunction"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/PCIeFunction.v1_2_3"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/PCIeFunctionCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Power"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Power.v1_6_1"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/PrivilegeRegistry"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/PrivilegeRegistry.v1_1_4"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Processor"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Processor.v1_12_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/ProcessorCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Resource"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Resource.v1_12_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Role"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Role.v1_2_5"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/RoleCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/SerialInterface"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/SerialInterface.v1_1_7"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/SerialInterfaceCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/ServiceRoot"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/ServiceRoot.v1_10_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Session"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Session.v1_3_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/SessionCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/SessionService"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/SessionService.v1_1_7"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/SimpleStorage"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/SimpleStorage.v1_2_1"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/SimpleStorageCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/SoftwareInventory"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/SoftwareInventory.v1_3_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/SoftwareInventoryCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Storage"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Storage.v1_8_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/StorageCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Task"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Task.v1_5_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/TaskCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/TaskService"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/TaskService.v1_1_5"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Thermal"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Thermal.v1_6_2"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/UpdateService"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/UpdateService.v1_9_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/VLanNetworkInterface"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/VLanNetworkInterface.v1_1_5"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/VLanNetworkInterfaceCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/VirtualMedia"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/VirtualMedia.v1_4_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/VirtualMediaCollection"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Volume"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/Volume.v1_5_0"
        },
        {
            "@odata.id": "/redfish/v1/JsonSchemas/VolumeCollection"
        }
    ],
    "Members@odata.count": 122
}

    # HTTP GET
    def get(self):
        logging.info('JsonSchemasCollectionAPI GET called')
        try:
            resp = self.config, 200
        except Exception:
            traceback.print_exc()
            resp = INTERNAL_SERVER_ERROR
        return resp

    # HTTP PUT
    def put(self):
        logging.info('JsonSchemasCollectionAPI PUT called')
        return 'PUT is not a supported command for JsonSchemasCollectionAPI', 405

    def verify(self, config):
        #TODO: Implement a method to verify that the POST body is valid
        return True,{}

    # HTTP POST
    def post(self):
        logging.info('JsonSchemasCollectionAPI POST called')
        return 'POST is not a supported command for JsonSchemasCollectionAPI', 405
 
    # HTTP PATCH
    def patch(self):
        logging.info('JsonSchemasCollectionAPI PATCH called')
        return 'PATCH is not a supported command for JsonSchemasCollectionAPI', 405

    # HTTP DELETE
    def delete(self):
        logging.info('JsonSchemasCollectionAPI DELETE called')
        return 'DELETE is not a supported command for JsonSchemasCollectionAPI', 405


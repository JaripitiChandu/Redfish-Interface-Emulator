# Copyright Notice:
# Copyright 2016-2019 DMTF. All rights reserved.
# License: BSD 3-Clause License. For full text see link: https://github.com/DMTF/Redfish-Interface-Emulator/blob/main/LICENSE.md

# Resource Manager Module

# External imports
import os
import json
import urllib3
from uuid import uuid4
from threading import Thread
import logging
import copy
# Local imports
import g
from . import utils
from .resource_dictionary import ResourceDictionary
from .static_loader import load_static
# Local imports (special case)
from .redfish.computer_system import ComputerSystem
from .redfish.computer_systems import ComputerSystemCollection
from .exceptions import CreatePooledNodeError, RemovePooledNodeError, EventSubscriptionError
from .redfish.event_service import EventService, Subscriptions
from .redfish.event import Event
# EventService imports
from .redfish.EventService_api import EventServiceAPI
from .redfish.Subscriptions_api import SubscriptionCollectionAPI, SubscriptionAPI
# Chassis imports
from .redfish.Chassis_api import ChassisCollectionAPI, ChassisAPI
from .redfish.power_api import PowerAPI
from .redfish.thermal_api import ThermalAPI
from .redfish.network_adapters_api import NetworkAdaptersCollectionAPI,NetworkAdaptersAPI
from .redfish.network_ports_api import NetworkPortsCollectionAPI, NetworkPortsAPI
from .redfish.network_device_functions_api import NetworkDeviceFunctionsCollectionAPI,NetworkDeviceFunctionsAPI
from .redfish.network_device_functions_metrics_api import NetworkDeviceFunctionsMetricsAPI
from .redfish.Fabrics_api import Fabrics, Fabric
# Manager imports
from .redfish.Manager_api import ManagerCollectionAPI, ManagerAPI, CreateManager
from .redfish.ethernet_interface_api import EthernetInterfaceCollectionAPI, EthernetInterfaceAPI
from .redfish.network_protocols_api import NetworkProtocolAPI
from .redfish.cisco_internal_storage_api import CiscoInternalStorageCollectionAPI, CiscoInternalStorageAPI
from .redfish.ciscopartition_api import CiscoPartitionAPI
from .redfish.ciscofile_api import CiscoFileCollectionAPI, CiscoFileAPI
from .redfish.VirtualMedia_api import VirtualMediaCollectionAPI, VirtualMediaAPI
from .redfish.SerialInterfaces_api import SerialInterfaces, SerialInterface
from .redfish.LogServices_api import LogServiceCollectionAPI, LogServiceAPI
from .redfish.LogEntry_api import LogEntryCollectionAPI, LogEntryAPI
from .redfish.ManagerResetAction_api import ManagerResetActionAPI
# EgResource imports
from .redfish.eg_resource_api import EgResourceCollectionAPI, EgResourceAPI, CreateEgResource
from .redfish.eg_subresource_api import EgSubResourceCollectionAPI, EgSubResourceAPI, CreateEgSubResource
# ComputerSystem imports
from .redfish.ComputerSystem_api import ComputerSystemCollectionAPI, ComputerSystemAPI, CreateComputerSystem
from .redfish.Bios_api import BiosAPI
from .redfish.SecureBoot_api import SecureBootAPI
from .redfish.processor_api import Processor, Processors
from .redfish.memory_api import MemoryAPI, MemoryCollectionAPI
from .redfish.simplestorage import SimpleStorage, SimpleStorageCollection
from .redfish.storage_api import StorageAPI, StorageCollectionAPI
from .redfish.ethernetinterface import EthernetInterfaceCollection, EthernetInterface
from .redfish.ResetActionInfo_api import ResetActionInfo_API
from .redfish.ResetAction_api import ResetAction_API
from .redfish.drive_api import DriveAPI
from .redfish.Volumes_api import Volumes, Volume
from .redfish.PCIeDevice_api import PCIeDeviceAPI
from .redfish.PCIeFunctions_api import PCIeFunction, PCIeFunctions
# PCIe Switch imports
from .redfish.pcie_switch_api import PCIeSwitchesAPI, PCIeSwitchAPI
# CompositionService imports
from .redfish.CompositionService_api import CompositionServiceAPI
from .redfish.ResourceBlock_api import ResourceBlockCollectionAPI, ResourceBlockAPI, CreateResourceBlock
from .redfish.ResourceZone_api import ResourceZoneCollectionAPI, ResourceZoneAPI, CreateResourceZone
# Update Service imports
from .redfish.updateservice_api import UpdateServiceAPI
from .redfish.firmware_inventory_api import FirmwareInventoryCollectionAPI, FirmwareInventoryAPI
from .redfish.software_inventory_api import SoftwareInventoryCollectionAPI, SoftwareInventoryAPI
# AccountService imports
from .redfish.AccountService_api import AccountServiceAPI
from .redfish.Accounts_api import Accounts, Account

mockupfolders = []

# The ResourceManager __init__ method sets up the static and dynamic
# resources.
#
# When a resource is accessed, the resource is sought in the following
# order:
#   1. Dynamic resources for specific URIs
#   2. Default dynamic resources
#   3. Static resource dictionary
#
# This allows specific resources to be implemented as dynamic resources
# while leaving the remainder of the URI path as static resources.
#
# Static resources are loaded from the ./redfish/static directory.
# This directory is a copy of the one of the ./mockups directories.
#
# Dynamic resources are attached to endpoints using the Flask-restful
# mechanism, not the Flask mechanism.
#   - This involves associating an API class to a resource endpoint.
#     A collection resource requires the association of the collection
#     resource and the member resource(s).
#   - Once the API is added, explicit calls can be made to one or more
#     singleton resources that have been populated.
#   - The EgResource* and EgSubResource* files provide examples of how
#     to add dynamic resources.
#
# Note: There is one additional change that needs to be made in order
# to create multiple instances of a resource. The resource endpoint
# for a second instance will collide with the first, because flask does
# not re-use endpoint names for subordinate resources. This results
# in an assertion error failure:
#   "AssertionError: View function mapping is overwriting an existing
#   endpoint function"
#
# The fix would be to form unique endpoint names and pass them in
# with the call to api_add_resource(), as shown in the following:
#   api.add_resource(Todo, '/todo/<int:todo_id>', endpoint='todo_ep')

class ResourceManager(object):
    """
    ResourceManager Class

    Load static resources and dynamic resources
    Defines ServiceRoot
    """

    def __init__(self, rest_base, spec, mode, trays=None):
        """
        Arguments:
            rest_base - Base URL for the REST interface
            spec      - Which spec to use, Redfish or Chinook
            trays     - (Optional) List of trays to initially load into the
                        resource manager
        When a resource is accessed, the resource is sought in the following order
        1. Dynamic resource for specific URI
        2. Static resource dictionary
        """

        self.rest_base = rest_base
        self.__config = None
        self.mode = mode
        self.spec = spec
        self.modified = utils.timestamp()
        self.uuid = str(uuid4())
        self.time = self.modified
        self.cs_puid_count = 0

        # Load the static resources into the dictionary

        self.resource_dictionary = ResourceDictionary()
        mockupfolders = copy.copy(g.staticfolders)

        if "Redfish" in mockupfolders:
            logging.info('Loading Redfish static resources')
            # self.AccountService =   load_static('AccountService', 'redfish', mode, rest_base, self.resource_dictionary)
            self.Registries =       load_static('Registries', 'redfish', mode, rest_base, self.resource_dictionary)
            self.SessionService =   load_static('SessionService', 'redfish', mode, rest_base, self.resource_dictionary)
            self.TaskService =      load_static('TaskService', 'redfish', mode, rest_base, self.resource_dictionary)

#        if "Swordfish" in mockupfolders:
#            self.StorageServices = load_static('StorageServices', 'redfish', mode, rest_base, self.resource_dictionary)
#            self.StorageSystems = load_static('StorageSystems', 'redfish', mode, rest_base, self.resource_dictionary)

        # Attach APIs for dynamic resources

        # EventService Resources
        g.api.add_resource(EventServiceAPI, '/redfish/v1/EventService',
                resource_class_kwargs={'rb': g.rest_base, 'id': "EventService"})
        # EventService SubResources
        g.api.add_resource(SubscriptionCollectionAPI, '/redfish/v1/EventService/Subscriptions')
        g.api.add_resource(SubscriptionAPI, '/redfish/v1/EventService/Subscriptions/<string:ident>',
                resource_class_kwargs={'rb': g.rest_base})

        # Chassis Resources
        g.api.add_resource(ChassisCollectionAPI, '/redfish/v1/Chassis')
        g.api.add_resource(ChassisAPI, '/redfish/v1/Chassis/<string:ident>',
                resource_class_kwargs={'rb': g.rest_base})
        # Chassis SubResources
        g.api.add_resource(ThermalAPI, '/redfish/v1/Chassis/<string:ident>/Thermal',
                resource_class_kwargs={'rb': g.rest_base})
        # Chassis SubResources
        g.api.add_resource(PowerAPI, '/redfish/v1/Chassis/<string:ident>/Power',
                resource_class_kwargs={'rb': g.rest_base})
        # Chassis SubResources
        g.api.add_resource(NetworkAdaptersCollectionAPI, '/redfish/v1/Chassis/<string:ident>/NetworkAdapters')
        g.api.add_resource(NetworkAdaptersAPI, '/redfish/v1/Chassis/<string:ident>/NetworkAdapters/<string:ident1>',
                resource_class_kwargs={'rb': g.rest_base})
        # Chassis SubResources
        g.api.add_resource(NetworkPortsCollectionAPI, '/redfish/v1/Chassis/<string:ident>/NetworkAdapters/<string:ident1>/NetworkPorts')
        g.api.add_resource(NetworkPortsAPI, '/redfish/v1/Chassis/<string:ident>/NetworkAdapters/<string:ident1>/NetworkPorts/<string:ident2>',
                resource_class_kwargs={'rb': g.rest_base})
        # Chassis SubResources
        g.api.add_resource(NetworkDeviceFunctionsCollectionAPI, '/redfish/v1/Chassis/<string:ident>/NetworkAdapters/<string:ident1>/NetworkDeviceFunctions')
        g.api.add_resource(NetworkDeviceFunctionsAPI, '/redfish/v1/Chassis/<string:ident>/NetworkAdapters/<string:ident1>/NetworkDeviceFunctions/<string:ident2>',
                resource_class_kwargs={'rb': g.rest_base})
        # Chassis SubResources
        g.api.add_resource(NetworkDeviceFunctionsMetricsAPI, '/redfish/v1/Chassis/<string:ident>/NetworkAdapters/<string:ident1>/NetworkDeviceFunctions/<string:ident2>/Metrics',
                resource_class_kwargs={'rb': g.rest_base})

        # Manager Resources
        g.api.add_resource(ManagerCollectionAPI, '/redfish/v1/Managers')
        g.api.add_resource(ManagerAPI, '/redfish/v1/Managers/<string:ident>', resource_class_kwargs={'rb': g.rest_base})
        #Manager SubResources
        g.api.add_resource(EthernetInterfaceCollectionAPI, '/redfish/v1/Managers/<string:ident>/EthernetInterfaces')
        g.api.add_resource(EthernetInterfaceAPI, '/redfish/v1/Managers/<string:ident>/EthernetInterfaces/<string:ident1>', resource_class_kwargs={'rb': g.rest_base})
        #Manager SubResources
        g.api.add_resource(NetworkProtocolAPI, '/redfish/v1/Managers/<string:ident>/NetworkProtocol')
        #Manager SubResources
        g.api.add_resource(CiscoInternalStorageCollectionAPI, '/redfish/v1/Managers/<string:ident>/Oem/CiscoInternalStorage')
        g.api.add_resource(CiscoInternalStorageAPI, '/redfish/v1/Managers/<string:ident>/Oem/CiscoInternalStorage/FlexMMC', resource_class_kwargs={'rb': g.rest_base})
        #Manager SubResources
        g.api.add_resource(CiscoPartitionAPI, '/redfish/v1/Managers/<string:ident>/Oem/CiscoInternalStorage/FlexMMC/CiscoPartition/<string:ident1>', resource_class_kwargs={'rb': g.rest_base})
        #Manager SubResources
        g.api.add_resource(CiscoFileCollectionAPI, '/redfish/v1/Managers/<string:ident>/Oem/CiscoInternalStorage/FlexMMC/CiscoPartition/<string:ident1>/CiscoFile')
        g.api.add_resource(CiscoFileAPI, '/redfish/v1/Managers/<string:ident>/Oem/CiscoInternalStorage/FlexMMC/CiscoPartition/<string:ident1>/CiscoFile/<string:ident2>', resource_class_kwargs={'rb': g.rest_base})
        #Manager SubResources
        g.api.add_resource(VirtualMediaCollectionAPI, '/redfish/v1/Managers/<string:ident>/VirtualMedia')
        g.api.add_resource(VirtualMediaAPI, '/redfish/v1/Managers/<string:ident1>/VirtualMedia/<int:ident2>')
        #Manager SubResources
        g.api.add_resource(SerialInterfaces, '/redfish/v1/Managers/<string:ident>/SerialInterfaces')
        g.api.add_resource(SerialInterface, '/redfish/v1/Managers/<string:ident1>/SerialInterfaces/<string:ident2>')
        #Manager SubResources
        g.api.add_resource(LogServiceCollectionAPI, '/redfish/v1/Managers/<string:ident>/LogServices')
        g.api.add_resource(LogServiceAPI, '/redfish/v1/Managers/<string:ident>/LogServices/<string:ident1>', resource_class_kwargs={'rb': g.rest_base})
        #Manager SubResources
        g.api.add_resource(LogEntryCollectionAPI, '/redfish/v1/Managers/<string:ident>/LogServices/<string:ident1>/Entries')
        g.api.add_resource(LogEntryAPI, '/redfish/v1/Managers/<string:ident>/LogServices/<string:ident1>/Entries/<string:ident2>', resource_class_kwargs={'rb': g.rest_base})
        #Manager SubResources
        g.api.add_resource(ManagerResetActionAPI, '/redfish/v1/Managers/<string:ident>/Actions/Manager.Reset', resource_class_kwargs={'rb': g.rest_base})
        # EgResource Resources (Example entries for attaching APIs)
        # g.api.add_resource(EgResourceCollectionAPI,
        #     '/redfish/v1/EgResources')
        # g.api.add_resource(EgResourceAPI,
        #     '/redfish/v1/EgResources/<string:ident>',
        #     resource_class_kwargs={'rb': g.rest_base})
        #
        # EgResource SubResources (Example entries for attaching APIs)
        # g.api.add_resource(EgSubResourceCollection,
        #     '/redfish/v1/EgResources/<string:ident>/EgSubResources',
        #     resource_class_kwargs={'rb': g.rest_base})
        # g.api.add_resource(EgSubResource,
        #     '/redfish/v1/EgResources/<string:ident1>/EgSubResources/<string:ident2>',
        #     resource_class_kwargs={'rb': g.rest_base})

        # Fabrics Resources
        g.api.add_resource(Fabrics, '/redfish/v1/Fabrics')
        g.api.add_resource(Fabric, '/redfish/v1/Fabrics/<string:ident>',
                resource_class_kwargs={'rb': g.rest_base})
        # System Resources
        g.api.add_resource(ComputerSystemCollectionAPI, '/redfish/v1/Systems')
        g.api.add_resource(ComputerSystemAPI, '/redfish/v1/Systems/<string:ident>',
                resource_class_kwargs={'rb': g.rest_base})
        # System SubResources
        g.api.add_resource(BiosAPI, "/redfish/v1/Systems/<string:ident>/Bios")
        # System SubResources
        g.api.add_resource(SecureBootAPI, "/redfish/v1/Systems/<string:ident>/SecureBoot")
        # System SubResources
        g.api.add_resource(Processors, '/redfish/v1/Systems/<string:ident>/Processors')
        g.api.add_resource(Processor, '/redfish/v1/Systems/<string:ident1>/Processors/<string:ident2>',
                '/redfish/v1/CompositionService/ResourceBlocks/<string:ident1>/Processors/<string:ident2>')
        # System SubResources
        g.api.add_resource(MemoryCollectionAPI, '/redfish/v1/Systems/<string:ident>/Memory')
        g.api.add_resource(MemoryAPI, '/redfish/v1/Systems/<string:ident1>/Memory/<string:ident2>',
                '/redfish/v1/CompositionService/ResourceBlocks/<string:ident1>/Memory/<string:ident2>')
        # System SubResources
        g.api.add_resource(SimpleStorageCollection, '/redfish/v1/Systems/<string:ident>/SimpleStorage',
                resource_class_kwargs={'rb': g.rest_base,'suffix':'Systems'})
        g.api.add_resource(SimpleStorage, '/redfish/v1/Systems/<string:ident1>/SimpleStorage/<string:ident2>',
                '/redfish/v1/CompositionService/ResourceBlocks/<string:ident1>/SimpleStorage/<string:ident2>')
        # System SubResources
        g.api.add_resource(StorageCollectionAPI, '/redfish/v1/Systems/<string:ident>/Storage')
        g.api.add_resource(StorageAPI, '/redfish/v1/Systems/<string:ident1>/Storage/<string:ident2>')
        # System SubResources
        g.api.add_resource(EthernetInterfaceCollection, '/redfish/v1/Systems/<string:ident>/EthernetInterfaces',
                resource_class_kwargs={'rb': g.rest_base,'suffix':'Systems'})
        g.api.add_resource(EthernetInterface, '/redfish/v1/Systems/<string:ident1>/EthernetInterfaces/<string:ident2>',
                '/redfish/v1/CompositionService/ResourceBlocks/<string:ident1>/EthernetInterfaces/<string:ident2>')
        # System SubResources
        g.api.add_resource(ResetActionInfo_API, '/redfish/v1/Systems/<string:ident>/ResetActionInfo',
                resource_class_kwargs={'rb': g.rest_base})
        g.api.add_resource(ResetAction_API, '/redfish/v1/Systems/<string:ident>/Actions/ComputerSystem.Reset',
                resource_class_kwargs={'rb': g.rest_base})
        # System SubResources
        g.api.add_resource(DriveAPI, '/redfish/v1/Systems/<string:ident1>/Storage/<string:ident2>/Drives/<int:ident3>')
        # System SubResources
        g.api.add_resource(Volumes, '/redfish/v1/Systems/<string:ident1>/Storage/<string:ident2>/Volumes')
        g.api.add_resource(Volume, '/redfish/v1/Systems/<string:ident1>/Storage/<string:ident2>/Volumes/<int:ident3>')
        # System SubResources
        g.api.add_resource(PCIeDeviceAPI, '/redfish/v1/Systems/<string:ident1>/PCIeDevices/<string:ident2>')
        # System SubResources
        g.api.add_resource(PCIeFunctions, '/redfish/v1/Systems/<string:ident1>/PCIeDevices/<string:ident2>/PCIeFunctions')
        g.api.add_resource(PCIeFunction, '/redfish/v1/Systems/<string:ident1>/PCIeDevices/<string:ident2>/PCIeFunctions/<int:ident3>')


        # PCIe Switch Resources
        g.api.add_resource(PCIeSwitchesAPI, '/redfish/v1/PCIeSwitches')
        g.api.add_resource(PCIeSwitchAPI, '/redfish/v1/PCIeSwitches/<string:ident>',
                resource_class_kwargs={'rb': g.rest_base})

        # Composition Service Resources
        g.api.add_resource(CompositionServiceAPI, '/redfish/v1/CompositionService',
                resource_class_kwargs={'rb': g.rest_base, 'id': "CompositionService"})
        # Composition Service SubResources
        g.api.add_resource(ResourceBlockCollectionAPI, '/redfish/v1/CompositionService/ResourceBlocks')
        g.api.add_resource(ResourceBlockAPI, '/redfish/v1/CompositionService/ResourceBlocks/<string:ident>',
                resource_class_kwargs={'rb': g.rest_base})
        # Composition Service SubResources
        g.api.add_resource(ResourceZoneCollectionAPI, '/redfish/v1/CompositionService/ResourceZones')
        g.api.add_resource(ResourceZoneAPI, '/redfish/v1/CompositionService/ResourceZones/<string:ident>',
                resource_class_kwargs={'rb': g.rest_base})
        #Update Service Resources
        g.api.add_resource(UpdateServiceAPI, '/redfish/v1/UpdateService')
        #Update Service SubResources
        g.api.add_resource(FirmwareInventoryCollectionAPI, '/redfish/v1/UpdateService/FirmwareInventory')
        g.api.add_resource(FirmwareInventoryAPI, '/redfish/v1/UpdateService/FirmwareInventory/<string:ident>',
                resource_class_kwargs={'rb': g.rest_base})
        #Update Service SubResources
        g.api.add_resource(SoftwareInventoryCollectionAPI, '/redfish/v1/UpdateService/SoftwareInventory')
        g.api.add_resource(SoftwareInventoryAPI, '/redfish/v1/UpdateService/SoftwareInventory/<string:ident>',
                resource_class_kwargs={'rb': g.rest_base})

        #AccountService Resource
        g.api.add_resource(AccountServiceAPI, "/redfish/v1/AccountService")
        #AccountService Subresources
        g.api.add_resource(Accounts, "/redfish/v1/AccountService/Accounts")
        g.api.add_resource(Account, "/redfish/v1/AccountService/Accounts/<int:ident>")

    @property
    def configuration(self):
        """
        Configuration property - Service Root
        """
        # config = {
        #     '@odata.context': self.rest_base + '$metadata#ServiceRoot',
        #     '@odata.type': '#ServiceRoot.1.0.0.ServiceRoot',
        #     '@odata.id': self.rest_base,
        #     'Id': 'RootService',
        #     'Name': 'Root Service',
        #     'RedfishVersion': '1.0.0',
        #     'UUID': self.uuid,
        #     'Chassis': {'@odata.id': self.rest_base + 'Chassis'},
        #     # 'EgResources': {'@odata.id': self.rest_base + 'EgResources'},
        #     'Managers': {'@odata.id': self.rest_base + 'Managers'},
        #     'TaskService': {'@odata.id': self.rest_base + 'TaskService'},
        #     'SessionService': {'@odata.id': self.rest_base + 'SessionService'},
        #     'AccountService': {'@odata.id': self.rest_base + 'AccountService'},
        #     'EventService': {'@odata.id': self.rest_base + 'EventService'},
        #     'Registries': {'@odata.id': self.rest_base + 'Registries'},
        #     'Systems': {'@odata.id': self.rest_base + 'Systems'},
        #     'CompositionService': {'@odata.id': self.rest_base + 'CompositionService'}
        # }

        return self.__config

    @configuration.setter
    def configuration(self, value):
        self.__config = value

    @property
    def available_procs(self):
        return self.max_procs - self.used_procs

    @property
    def available_mem(self):
        return self.max_memory - self.used_memory

    @property
    def available_storage(self):
        return self.max_storage - self.used_storage

    @property
    def available_network(self):
        return self.max_network - self.used_network

    @property
    def num_pooled_nodes(self):
        if self.spec == 'Chinook':
            return self.PooledNodes.count
        else:
            return self.Systems.count

    def _create_redfish(self, rs, action):
        """
        Private method for creating a Redfish based pooled node

        Arguments:
            rs  - The requested pooled node
        """
        try:
            pn = ComputerSystem(rs, self.cs_puid_count + 1, self.rest_base, 'Systems')
            self.Systems.add_computer_system(pn)
        except KeyError as e:
            raise CreatePooledNodeError(
                'Configuration missing key: ' + e.message)
        try:
            # Verifying resources
            assert pn.processor_count <= self.available_procs, self.err_str.format('CPUs')
            assert pn.storage_gb <= self.available_storage, self.err_str.format('storage')
            assert pn.network_ports <= self.available_network, self.err_str.format('network ports')
            assert pn.total_memory_gb <= self.available_mem, self.err_str.format('memory')

            self.used_procs += pn.processor_count
            self.used_storage += pn.storage_gb
            self.used_network += pn.network_ports
            self.used_memory += pn.total_memory_gb
        except AssertionError as e:
            self._remove_redfish(pn.cs_puid)
            raise CreatePooledNodeError(e.message)
        except KeyError as e:
            self._remove_redfish(pn.cs_puid)
            raise CreatePooledNodeError(
                'Requested system missing key: ' + e.message)

        self.resource_dictionary.add_resource('Systems/{0}'.format(pn.cs_puid), pn)
        self.cs_puid_count += 1
        return pn.configuration

    def _remove_redfish(self, cs_puid):
        """
        Private method for removing a Redfish based pooled node

        Arguments:
            cs_puid - CS_PUID of the pooled node to remove
        """
        try:
            pn = self.Systems[cs_puid]

            # Adding back in used resources
            self.used_procs -= pn.processor_count
            self.used_storage -= pn.storage_gb
            self.used_network -= pn.network_ports
            self.used_memory -= pn.total_memory_gb

            self.Systems.remove_computer_system(pn)
            self.resource_dictionary.delete_resource('Systems/{0}'.format(cs_puid))

            if self.Systems.count == 0:
                self.cs_puid_count = 0
        except IndexError:
            raise RemovePooledNodeError(
                'No pooled node with CS_PUID: {0}, exists'.format(cs_puid))

    def get_resource(self, path):
        """
        Call Resource_Dictionary's get_resource
        """
        obj = self.resource_dictionary.get_resource(path)
        return obj


'''
    def remove_pooled_node(self, cs_puid):
        """
        Delete the specified pooled node and free its resources.

        Throws a RemovePooledNodeError Exception if a problem is encountered.

        Arguments:
            cs_puid - CS_PUID of the pooed node to remove
        """
        self.remove_method(cs_puid)

    def update_cs(self,cs_puid,rs):
        """
            Updates the power metrics of Systems/1
        """
        cs=self.Systems[cs_puid]
        cs.reboot(rs)
        return cs.configuration

    def update_system(self,rs,c_id):
        """
            Updates selected System
        """
        self.Systems[c_id].update_config(rs)

        event = Event(eventType='ResourceUpdated', severity='Notification', message='System updated',
                      messageID='ResourceUpdated.1.0.System', originOfCondition='/redfish/v1/System/{0}'.format(c_id))
        self.push_event(event, 'ResourceUpdated')
        return self.Systems[c_id].configuration

    def add_event_subscription(self, rs):
        destination = rs['Destination']
        types = rs['Types']
        context = rs['Context']

        allowedTypes = ['StatusChange',
                        'ResourceUpdated',
                        'ResourceAdded',
                        'ResourceRemoved',
                        'Alert']

        for type in types:
            match = False
            for allowedType in allowedTypes:
                if type == allowedType:
                    match = True

            if not match:
                raise EventSubscriptionError('Some of types are not allowed')

        es = self.EventSubscriptions.add_subscription(destination, types, context)
        es_id = es.configuration['Id']
        self.resource_dictionary.add_resource('EventService/Subscriptions/{0}'.format(es_id), es)
        event = Event()
        self.push_event(event, 'Alert')
        return es.configuration

    def push_event(self, event, type):
        # Retreive subscription list
        subscriptions = self.EventSubscriptions.configuration['Members']
        for sub in subscriptions:
            # Get event subscription
            event_channel = self.resource_dictionary.get_object(sub.replace('/redfish/v1/', ''))
            event_types = event_channel.configuration['EventTypes']
            dest_uri = event_channel.configuration['Destination']

            # Check if client subscribes for event type
            match = False
            for event_type in event_types:
                if event_type == type:
                    match = True

            if match:
                # Sending event response
                EventWorker(dest_uri, event).start()


class EventWorker(Thread):
    """
    Worker class for sending event messages to clients
    """
    def __init__(self, dest_uri, event):
        super(EventWorker, self).__init__()
        self.dest_uri = dest_uri
        self.event = event

    def run(self):
        try:
            request = urllib2.Request(self.dest_uri)
            request.add_header('Content-Type', 'application/json')
            urllib2.urlopen(request, json.dumps(self.event.configuration), 15)
        except Exception:
            pass
'''

from __future__ import annotations

import typing as ty

from ironic.common import boot_devices, exception
from ironic.conductor import task_manager
from ironic.drivers import base
from requests.sessions import Session

from ironic_driver_amt._glue import (
    BOOT_DEVICE_MAP,
    parse_driver_info,
)
from ironic_driver_amt.amt import wsman
from ironic_driver_amt.amt.wsman._requests import post
from ironic_driver_amt.amt.wsman.constants import role
from ironic_driver_amt.common import REQUIRED_PROPERTIES

if ty.TYPE_CHECKING:
    from ironic.conductor.task_manager import TaskManager
    from ironic.objects.node import Node

    BootDevice = ty.Literal['pxe', 'disk', 'cdrom', 'bios', 'safe', 'wanboot', 'iscsiboot', 'floppy', "uefihttp"]


class AMTManagement(base.ManagementInterface):
    def get_properties(self):
        return REQUIRED_PROPERTIES.copy()

    def validate(self, task):
        pass

    def get_sensors_data(self, task):
        return {}
    
    def get_supported_boot_devices(self, task: TaskManager):
        # node: Node = task.node # type: ignore # TODO: figure out boot to bios
        return list(BOOT_DEVICE_MAP.keys()) # skip bios for now
        # return amt.get_supported_boot_devices(parse_driver_info(node))
    
    @task_manager.require_exclusive_lock
    def set_boot_device(self, task: TaskManager, device: BootDevice, persistent=False):
        node: Node = task.node # type: ignore
        if device not in self.get_supported_boot_devices(task):
            msg = f"set_boot_device called with invalid device {device} for node {node.uuid}" # type: ignore
            raise exception.InvalidParameterValue(msg)

        node.set_driver_internal_info("amt_boot_device", device)
        client = parse_driver_info(node)
        with Session() as s:
            if persistent:
                node.set_driver_internal_info("amt_boot_persistent", True)
            else:
                xml = wsman.CIM_BootService.SetBootConfigRole(role.IS_NEXT_SINGLE_USE)
                post(client, xml, s)

            xml = wsman.CIM_BootConfigSetting.ChangeBootOrder([device]) # type: ignore
            post(client,xml, s)
    
    def get_boot_device(self, task: TaskManager):
        boot_device = task.node.driver_internal_info.get("amt_boot_device") # type: ignore
        persistent = task.node.driver_internal_info.get("persistent") # type: ignore
        
        return { 
            "boot_device": boot_device or boot_devices.DISK, 
            "persistent": persistent or False 
        }
    
    
from __future__ import annotations

import typing as ty
from xml.etree import ElementTree

from ironic.common import states
from ironic.conductor import task_manager, utils
from ironic.drivers import base
from oslo_log import log
from requests.sessions import Session

from ironic_driver_amt._glue import (
    GET_POWER_STATE_MAP,
    SET_POWER_STATE_MAP,
    parse_driver_info,
)
from ironic_driver_amt.amt import wsman
from ironic_driver_amt.amt.wsman._requests import post
from ironic_driver_amt.common import REQUIRED_PROPERTIES

if ty.TYPE_CHECKING:
    from logging import Logger

    from ironic.common import states
    from ironic.conductor.task_manager import TaskManager
    from ironic.objects.node import Node


LOG: Logger = log.getLogger("ironic.drivers.amt." + __name__)
LOG.setLevel(log.DEBUG)


class AMTPower(base.PowerInterface):

    def get_properties(self):
        return REQUIRED_PROPERTIES.copy()

    def validate(self, task):
        pass

    def get_power_state(self, task: TaskManager):
        LOG.debug("get_power_state called")
        node: Node = task.node # type: ignore

        # return amt.get_power_state(parse_driver_info(node))
        xml = wsman.CIM_AssociatedPowerManagementService.Get() # type: ignore
        result = post(parse_driver_info(node), xml)
        element = ElementTree.fromstring(result).find(
            f".//{{{wsman.CIM_AssociatedPowerManagementService.ResourceURI}}}PowerState"
        )
        if element is not None and element.text is not None:
            return GET_POWER_STATE_MAP[int(element.text)]
        else:
            raise Exception("Response from wsman didn't include PowerState element")
        
    def _power_change(self, task: TaskManager, power_state: str, timeout):
        LOG.debug("_power_change called")
        node: Node = task.node # type: ignore
        client = parse_driver_info(node)
        with Session() as s:
            if power_state in (states.POWER_ON, states.REBOOT, states.SOFT_REBOOT) and node.driver_internal_info.get("amt_boot_persistent"): # type: ignore
                # Ensure boot device config persists with each boot/reboot
                xml = wsman.CIM_BootService.SetBootConfigRole()
                result = post(client, xml, s)
                LOG.debug(f"SetBootConfigRole: {result}")

            # return amt.set_power_state(client, POWER_STATE_MAP[power_state])
            xml = wsman.CIM_PowerManagementService.RequestPowerStateChange(SET_POWER_STATE_MAP[power_state])
            post(client, xml, s)
            LOG.debug(f"RequestPowerStateChange: {result}")
        utils.node_wait_for_power_state(task, power_state, timeout)

    @task_manager.require_exclusive_lock
    def set_power_state(self, task: TaskManager, power_state: str, timeout: int | None = None):
        LOG.debug("set_Power_state called")
        self._power_change(task, power_state, timeout)
    
    @task_manager.require_exclusive_lock
    def reboot(self, task: TaskManager, timeout: int | None = None):
        LOG.debug("reboot called")
        self._power_change(task, states.REBOOT, timeout)
        # TODO: Support going back from mgmt
    
    @task_manager.require_exclusive_lock
    def get_supported_power_states(self, task: TaskManager):
        LOG.debug("get_supported_power_states called")
        # node: Node = task.node # type: ignore

        # xml = wsman.CIM_AssociatedPowerManagementService.Get() # type: ignore
        # result = post(parse_driver_info(node), xml)
        # elements = (ElementTree
        #         .fromstring(result)
        #         .findall(f".//{{{wsman.CIM_AssociatedPowerManagementService.ResourceURI}}}AvailableRequestedPowerStates")
        # )
        return list(GET_POWER_STATE_MAP.values())
        # return [ GET_POWER_STATE_MAP[int(el.text)] for el in elements if el is not None and el.text is not None ]


from __future__ import annotations

import typing as ty

from ironic.common import boot_devices, states
from oslo_log import log

from ironic_driver_amt.amt.wsman.constants import boot_source, power

if ty.TYPE_CHECKING:
    from logging import Logger

    from ironic.objects.node import Node

    from ironic_driver_amt.amt.wsman._requests import ConnectionDetails

LOG: Logger = log.getLogger("ironic.drivers.amt." + __name__ )

GET_POWER_STATE_MAP = {
    power.POWER_ON: states.POWER_ON,
    power.POWER_OFF: states.POWER_OFF,
    power.REBOOT: states.REBOOT,
    power.SOFT_RESET: states.SOFT_REBOOT,
    power.SOFT_POWER_OFF: states.SOFT_POWER_OFF,
}

SET_POWER_STATE_MAP = {v: k for k,v in GET_POWER_STATE_MAP.items()}

BOOT_DEVICE_MAP = {
    boot_devices.CDROM: boot_source.CD,
    boot_devices.DISK: boot_source.DISK,
    boot_devices.PXE: boot_source.PXE,
}

def parse_driver_info(node: Node) -> ConnectionDetails:
    driver_info: dict = node.driver_info # type: ignore
    url = driver_info.get("amt_address")
    username = driver_info.get("amt_username")
    password = driver_info.get("amt_password")
    # TODO: Validate and handle insecure option
    
    creds: ConnectionDetails = {
        "url": url,
        "username": username,
        "password": password,
        "insecure": True,
    }

    return creds

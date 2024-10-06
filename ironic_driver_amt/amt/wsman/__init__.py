# ruff: noqa: F403
import importlib

from ironic_driver_amt.amt.wsman._base import AMT_ManagedElement, CIM_ManagedElement

__all__ = (
    "CIM_PowerManagementService",
    "CIM_BootConfigSetting",
    "CIM_BootService",
    # No dedicated Implementation
    "AMT_BootCapabilities",
    "CIM_AssociatedPowerManagementService",
    "CIM_NetworkPort",
)



def __getattr__(attr: str):

    if attr.startswith("AMT"):
        if attr in __all__[3:]:
            return type(attr , (AMT_ManagedElement, ), {})
        else:
            amt = importlib.import_module("ironic_driver_amt.amt.wsman._amt")
            return getattr(amt, attr)

    if attr.startswith("CIM"):
        if attr in __all__[3:]:
            return type(attr , (CIM_ManagedElement, ), {})
        else:
            cim = importlib.import_module("ironic_driver_amt.amt.wsman._cim")
            return getattr(cim, attr)

    raise AttributeError(attr)

def __dir__():
    return __all__
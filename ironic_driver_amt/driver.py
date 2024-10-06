from __future__ import annotations

from ironic.drivers import generic

from ironic_driver_amt.management import AMTManagement
from ironic_driver_amt.power import AMTPower

"""
Hardware type for Intel® Active Management Technology
"""

class AMTHardware(generic.GenericHardware):
    """AMT hardware type."""    

    @property
    def supported_management_interfaces(self):
        return [AMTManagement]

    @property
    def supported_power_interfaces(self):
        return [AMTPower]



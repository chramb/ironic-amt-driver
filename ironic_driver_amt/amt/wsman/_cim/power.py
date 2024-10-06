from __future__ import annotations

from ironic_driver_amt.amt.wsman._base import CIM_ManagedElement, payload, selector
from ironic_driver_amt.amt.wsman.constants import power


class CIM_PowerManagementService(CIM_ManagedElement):
  @classmethod
  def RequestPowerStateChange(cls, state: power.STATE):
    body = \
f"""
  <s:Body>
    <cim:RequestPowerStateChange_INPUT>
      <cim:PowerState>{state}</cim:PowerState>
      <cim:ManagedElement>
        <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
        <wsa:ReferenceParameters>
          <wsman:ResourceURI>{cls.NS}CIM_ComputerSystem</wsman:ResourceURI>
          {selector("ManagedSystem")}
        </wsa:ReferenceParameters>
      </cim:ManagedElement>
    </cim:RequestPowerStateChange_INPUT>
  </s:Body>\
"""
    return payload(
        resource=cls.ResourceURI, # type: ignore
        action=cls.ResourceURI + "/RequestPowerStateChange", # type: ignore
        extra_namespaces=f'xmlns:cim="{cls.ResourceURI}"',
        extra_headers=selector("Intel(r) AMT Power Management Service"),
        body=body,
    )

        
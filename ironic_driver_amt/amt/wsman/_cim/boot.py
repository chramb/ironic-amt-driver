
from ironic_driver_amt.amt.wsman._base import CIM_ManagedElement, payload, selector
from ironic_driver_amt.amt.wsman.constants import role


class CIM_BootConfigSetting(CIM_ManagedElement):
    @classmethod
    def ChangeBootOrder(cls, sources: list[str]):
        body = \
"""\
  <s:Body>
    <cim:ChangeBootOrder_INPUT>
"""
        for s in sources:
            src = \
f"""
      <cim:Source>
        <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
        <wsa:ReferenceParameters>
          <wsman:ResourceURI>http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/CIM_BootSourceSetting</wsman:ResourceURI>
          {selector(s, name="InstanceID")}
        </wsa:ReferenceParameters>
      </cim:Source>
"""
            body += src
        
        body += \
"""
    </cim:ChangeBootOrder_INPUT>
  </s:Body>
"""
        return payload(
            resource=cls.ResourceURI, # type: ignore
            action=cls.ResourceURI + "/ChangeBootOrder", # type: ignore
            extra_namespaces=f'xmlns:cim="{cls.ResourceURI}"',
            extra_headers=selector("Intel(r) AMT: Boot Configuration 0",name="InstanceID"),
            body=body,
        )


class CIM_BootService(CIM_ManagedElement):

    @classmethod
    def SetBootConfigRole(cls, role: int = role.IS_NEXT_SINGLE_USE):
        instance_id = "Intel(r) AMT: Boot Configuration 0"
        body = \
f"""
<s:Body>
  <cim:SetBootConfigRole_INPUT>
    <cim:BootConfigSetting>
      <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
      <wsa:ReferenceParameters>
        <wsman:ResourceURI>{CIM_BootConfigSetting.ResourceURI}</wsman:ResourceURI>
        {selector(instance_id, "InstanceID")}
      </wsa:ReferenceParameters>
    </cim:BootConfigSetting>
    <cim:Role>{role}</cim:Role>
  </cim:SetBootConfigRole_INPUT>
</s:Body>
"""
        return payload(
            resource=cls.ResourceURI, # type: ignore
            action=f'{cls.ResourceURI}/SetBootConfigRole',
            extra_namespaces=f'xmlns:cim="{cls.ResourceURI}"',
            extra_headers=selector("Intel(r) AMT Boot Service"),
            body=body
        )

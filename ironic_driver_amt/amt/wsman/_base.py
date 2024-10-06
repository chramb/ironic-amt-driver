from __future__ import annotations

import uuid

from ironic_driver_amt.amt.wsman.constants import namespace

namespaces = \
"""\
  xmlns:s="http://www.w3.org/2003/05/soap-envelope"
  xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing"
  xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd"{extra_namespaces}
"""

header = \
"""\
  <s:Header>
    <wsa:Action s:mustUnderstand="true">{action}</wsa:Action>
    <wsa:To s:mustUnderstand="true">/wsman</wsa:To>
    <wsman:ResourceURI s:mustUnderstand="true">{resource}</wsman:ResourceURI>
    <wsa:MessageID s:mustUnderstand="true">{message_id}</wsa:MessageID>
    <wsa:ReplyTo>
      <wsa:Address>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:Address>
    </wsa:ReplyTo>{extra_headers}
  </s:Header>
"""

envelope =\
"""
<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope 
{namespaces}>
{header}{body}
</s:Envelope>
"""
def selector(text: str, name: str = "Name") -> str:
    return f'<wsman:SelectorSet><wsman:Selector Name="{name}">{text}</wsman:Selector></wsman:SelectorSet>'


def payload(
        *,
        resource: str,
        action: str = "http://schemas.xmlsoap.org/ws/2004/09/transfer/Get",
        message_id: str = str(uuid.uuid4()),
        extra_namespaces: str = "",
        extra_headers: str = "",
        body: str = "  <s:Body/>",
) -> str:
    return envelope.format(
        namespaces=namespaces.format(
            extra_namespaces=extra_namespaces
        ),
        header=header.format(
            action=action,
            resource=resource,
            message_id=message_id,
            extra_headers=extra_headers,
        ),
        body=body
    )



class ManagedElement(type):
    NS: str

    def __getattr__(cls, attr):
        if attr == "ResourceURI":
            return cls.NS + cls.__name__

        if attr == "Get":
            def Get():
                return payload(
                        resource=cls.ResourceURI, # type: ignore
                    )
            
            return Get # type: ignore
        
        raise AttributeError(f"'{cls.__name__}' class has no attribute '{attr}'")
    

class CIM_ManagedElement(metaclass=ManagedElement):
    NS = namespace.CIM

class AMT_ManagedElement(metaclass=ManagedElement):
    NS = namespace.AMT
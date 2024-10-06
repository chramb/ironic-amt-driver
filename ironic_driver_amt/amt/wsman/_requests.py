from __future__ import annotations

import typing as ty

import requests.auth

if ty.TYPE_CHECKING:
    import requests.sessions

    class ConnectionDetails(ty.TypedDict):
        url: str
        username: str
        password: str
        insecure: bool

def post(
        client: ConnectionDetails,
        data: str,
        session: ty.Union[requests.sessions.Session, None] = None,
    ):
    if session is None:
        session = requests.sessions.Session()

    result = session.post(
        url= client["url"] + "/wsman",
        headers={'content-type': 'application/soap+xml;charset=UTF-8'},
        data=data,
        auth=requests.auth.HTTPDigestAuth(username=client["username"], password=client["password"]),
        verify=not client["insecure"]
    )

    # TODO Error handling

    return result.content

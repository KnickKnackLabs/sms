"""SMS Things"""

import asyncio

from xmpp import SMSClient, XMPPEvent

from sms.contacts import Contact as Contact


def wait_ready(client: SMSClient) -> asyncio.Future[None]:
    fut: asyncio.Future[None] = asyncio.get_event_loop().create_future()

    def on_start(_event: object) -> None:
        if not fut.done():
            fut.set_result(None)

    client.add_event_handler(
        XMPPEvent.SESSION_START,
        on_start,
        disposable=True,
    )

    def on_auth_failure(_event: object) -> None:
        if not fut.done():
            fut.set_exception(PermissionError("XMPP authentication failed"))

    client.add_event_handler(
        XMPPEvent.FAILED_AUTH,
        on_auth_failure,
        disposable=True,
    )

    return fut

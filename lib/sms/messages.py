import asyncio
from collections.abc import AsyncGenerator, AsyncIterator
from dataclasses import dataclass
from typing import cast, override

import slixmpp
from slixmpp import JID, Message as XMPPMessage
from slixmpp.plugins.xep_0203.stanza import Delay
from slixmpp.plugins.xep_0297.stanza import Forwarded
from slixmpp.plugins.xep_0313.stanza import MAM
from xmpp import XEP_0313, SMSClient, XMPPEvent


async def send_message(
    client: SMSClient,
    to: JID,
    body: str,
) -> None:

    client.send_message(
        mto=to,
        mbody=body,
        mtype="chat",
    )


@dataclass(frozen=True)
class Message:
    sender: str
    recipient: str
    body: str
    timestamp: str

    @override
    def __str__(self) -> str:
        heading = self.sender

        if self.timestamp:
            heading = f"[{self.timestamp}] {heading}"

        return f"{heading}\n {self.body}"

    def is_empty(self) -> bool:
        return not self.body.strip()

    def to_dict(self) -> dict[str, str]:
        return {
            "from": self.sender,
            "to": self.recipient,
            "body": self.body,
            "timestamp": self.timestamp,
        }


async def list_messages(
    client: SMSClient,
    limit: int = 20,
) -> list[Message]:
    archive = client.plugin[XEP_0313]

    rsm = {"max": limit}

    pages = archive.retrieve(
        rsm=rsm,
        iterator=True,
        reverse=True,
    )

    pages = cast(object, pages)
    it = cast(AsyncIterator[slixmpp.Iq], pages)

    async for page in it:
        archive = cast(MAM, page["mam"])

        stanzas = archive.get_results()
        msgs = map(to_message, stanzas)

        # skip empty messages
        msgs = filter(
            lambda msg: not msg.is_empty(),
            msgs,
        )

        return list(msgs)

    return []


def to_message(msg: XMPPMessage) -> Message:
    timestamp = ""

    if "mam_result" in msg:
        forwarded = cast(
            Forwarded,
            msg["mam_result"]["forwarded"],
        )

        msg = cast(XMPPMessage, forwarded.get_stanza())

        delay = cast(Delay, forwarded["delay"])
        stamp = delay.get_stamp()  # pyright: ignore[reportUnknownVariableType]
        timestamp = str(stamp) if stamp else ""  # pyright: ignore[reportUnknownArgumentType]

    return Message(
        sender=str(msg.get_from()),
        recipient=str(msg.get_to()),
        body=cast(str, msg["body"]),
        timestamp=timestamp,
    )


async def listen_for_messages(client: SMSClient) -> AsyncGenerator[Message]:
    queue: asyncio.Queue[XMPPMessage | None] = asyncio.Queue()

    client.add_event_handler(
        XMPPEvent.MESSAGE,
        queue.put_nowait,
    )

    def on_disconnected(_event: object) -> None:
        queue.put_nowait(None)

    client.add_event_handler(
        XMPPEvent.DISCONNECTED,
        on_disconnected,
    )

    try:
        client.send_presence()

        while True:
            msg = await queue.get()

            if msg is None:
                raise ConnectionError("XMPP connection closed")

            if msg["type"] not in ("chat", "normal"):
                continue

            message = to_message(msg)

            if message.is_empty():
                continue

            yield message

    finally:
        client.del_event_handler(
            XMPPEvent.MESSAGE,
            queue.put_nowait,
        )

        client.del_event_handler(
            XMPPEvent.DISCONNECTED,
            on_disconnected,
        )

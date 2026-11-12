"""Shared XMPP client logic for jmp.chat SMS integration."""

import asyncio
import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from datetime import datetime, timezone
from enum import StrEnum
from typing import cast

import slixmpp
from slixmpp.plugins.xep_0203.stanza import Delay
from slixmpp.plugins.xep_0297.stanza import Forwarded
from slixmpp.plugins.xep_0313.stanza import MAM

log = logging.getLogger(__name__)


XEP_0030 = "xep_0030"  # Service Discovery
XEP_0313 = "xep_0313"  # Archive (MAM)
XEP_0441 = "xep_0441"  # Preferences


class XMPPEvent(StrEnum):
    SESSION_START = "session_start"
    FAILED_AUTH = "failed_auth"
    MESSAGE = "message"
    DISCONNECTED = "disconnected"


class SMSClient(slixmpp.ClientXMPP):
    """XMPP client for sending and receiving SMS via jmp.chat."""

    def __init__(self, jid: str, password: str) -> None:
        super().__init__(jid, password)
        self.register_plugin(XEP_0030)  # Service Discovery
        self.register_plugin(XEP_0313)  # Message Archive Management (MAM)

    async def connect_and_run[T](
        self,
        callback: Callable[["SMSClient"], Awaitable[T]],
    ) -> T:
        """Connect, run a callback, then disconnect."""
        _ = self.connect()

        try:
            result = await callback(self)

        finally:
            _ = await self.disconnect()

        return result


async def check_connection(jid: str, password: str) -> bool:
    """Verify XMPP credentials by connecting and disconnecting."""
    client = SMSClient(jid, password)

    connected: asyncio.Future[bool] = asyncio.get_event_loop().create_future()

    def on_session_start(_event: object) -> None:
        connected.set_result(True)

    def on_failed_auth(_event: object) -> None:
        if not connected.done():
            connected.set_result(False)

    client.add_event_handler("session_start", on_session_start)
    client.add_event_handler("failed_auth", on_failed_auth)

    _ = client.connect()

    try:
        result = await asyncio.wait_for(connected, timeout=10)

    except TimeoutError:
        result = False

    finally:
        _ = await client.disconnect()

    return result


async def listen_messages(
    jid: str,
    password: str,
    callback: Callable[[dict[str, str]], None],
    timeout: float = 60,
    announce: bool = True,
) -> None:
    """Connect and listen for incoming messages in real-time."""
    client = SMSClient(jid, password)

    def on_message(msg: slixmpp.Message) -> None:
        body = cast(str, msg["body"])

        if msg["type"] in ("chat", "normal") and body:
            callback(
                {
                    "from": str(msg.get_from()),
                    "to": str(msg.get_to()),
                    "body": body,
                }
            )

    client.add_event_handler("message", on_message)

    async def on_session_start(_event: object) -> None:
        client.send_presence()
        _ = await client.get_roster()

        if announce:
            print(
                f"Listening ({timeout}s)..." if timeout else "Listening...", flush=True
            )

    client.add_event_handler("session_start", on_session_start)

    _ = client.connect()

    try:
        if timeout:
            await asyncio.sleep(timeout)

        else:
            await asyncio.Future()  # block forever

    except (KeyboardInterrupt, asyncio.CancelledError):
        pass

    finally:
        _ = await client.disconnect()


async def wait_for_message(
    jid: str,
    password: str,
    from_number: str | None = None,
    timeout: float = 300,
) -> dict[str, str] | None:
    """Wait for a single incoming message, optionally filtered by sender."""
    client = SMSClient(jid, password)
    result: asyncio.Future[dict[str, str] | None] = (
        asyncio.get_event_loop().create_future()
    )

    def on_message(msg: slixmpp.Message) -> None:
        if result.done():
            return

        body = cast(str, msg["body"])

        if msg["type"] not in ("chat", "normal") or not body:
            return

        sender = str(msg.get_from())

        if from_number:
            normalized = normalize_number(from_number)
            sender_local = sender.split("@")[0] if "@" in sender else sender

            if sender_local != normalized:
                return

        result.set_result(
            {
                "from": sender,
                "to": str(msg.get_to()),
                "body": body,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def on_failed_auth(_event: object) -> None:
        if not result.done():
            result.set_result(None)

    client.add_event_handler("message", on_message)
    client.add_event_handler("failed_auth", on_failed_auth)

    async def on_session_start(_event: object) -> None:
        client.send_presence()
        _ = await client.get_roster()

    client.add_event_handler("session_start", on_session_start)

    _ = client.connect()

    try:
        msg = await asyncio.wait_for(result, timeout=timeout)
        return msg

    except TimeoutError:
        return None

    finally:
        _ = await client.disconnect()


def is_jid(value: str) -> bool:
    """Check if a value looks like an XMPP JID rather than a phone number."""
    return any(c.isalpha() for c in value)


def normalize_number(number: str) -> str:
    """Normalize a phone number to digits only with leading +1 if needed."""
    digits = "".join(c for c in number if c.isdigit() or c == "+")

    if not digits.startswith("+"):
        if len(digits) == 10:
            digits = "+1" + digits

        elif len(digits) == 11 and digits.startswith("1"):
            digits = "+" + digits

    return digits

"""Shared XMPP client logic for jmp.chat SMS integration."""

import asyncio
import logging

import slixmpp

log = logging.getLogger(__name__)


class SMSClient(slixmpp.ClientXMPP):
    """XMPP client for sending and receiving SMS via jmp.chat."""

    def __init__(self, jid, password):
        super().__init__(jid, password)
        self.register_plugin("xep_0030")  # Service Discovery
        self.register_plugin("xep_0313")  # Message Archive Management (MAM)

    async def connect_and_run(self, callback):
        """Connect, run a callback, then disconnect."""
        self.connect()
        try:
            result = await callback(self)
        finally:
            self.disconnect()
        return result


async def check_connection(jid, password):
    """Verify XMPP credentials by connecting and disconnecting."""
    client = SMSClient(jid, password)
    connected = asyncio.get_event_loop().create_future()

    def on_session_start(event):
        connected.set_result(True)

    def on_failed_auth(event):
        if not connected.done():
            connected.set_result(False)

    client.add_event_handler("session_start", on_session_start)
    client.add_event_handler("failed_auth", on_failed_auth)

    client.connect()

    try:
        result = await asyncio.wait_for(connected, timeout=10)
    except asyncio.TimeoutError:
        result = False
    finally:
        client.disconnect()

    return result


async def send_sms(jid, password, to_number, message):
    """Send an SMS message via jmp.chat.

    jmp.chat routes XMPP messages to SMS when sent to <number>@cheogram.com.
    """
    client = SMSClient(jid, password)
    sent = asyncio.get_event_loop().create_future()

    def on_session_start(event):
        # jmp.chat gateway address for SMS
        sms_jid = normalize_number(to_number) + "@cheogram.com"
        client.send_message(mto=sms_jid, mbody=message, mtype="chat")
        sent.set_result(True)

    client.add_event_handler("session_start", on_session_start)

    client.connect()

    try:
        result = await asyncio.wait_for(sent, timeout=10)
    except asyncio.TimeoutError:
        result = False
    finally:
        client.disconnect()

    return result


async def read_messages(jid, password, limit=20):
    """Read recent messages from the XMPP message archive (MAM)."""
    client = SMSClient(jid, password)
    messages = []
    done = asyncio.get_event_loop().create_future()

    async def on_session_start(event):
        try:
            results = client.plugin["xep_0313"]
            iq = await results.retrieve(rsm={"max": limit, "before": ""})

            for msg in iq["mam"]["results"]:
                forwarded = msg["mam_result"]["forwarded"]
                message = forwarded["stanza"]
                delay = forwarded["delay"]
                body = message["body"]
                if body:
                    messages.append({
                        "from": str(message["from"]),
                        "to": str(message["to"]),
                        "body": str(body),
                        "timestamp": str(delay["stamp"]) if delay["stamp"] else "",
                    })
        except Exception as e:
            log.error("Failed to retrieve messages: %s", e)
        finally:
            done.set_result(True)

    client.add_event_handler("session_start", on_session_start)

    client.connect()

    try:
        await asyncio.wait_for(done, timeout=15)
    except asyncio.TimeoutError:
        log.error("Timed out waiting for messages")
    finally:
        client.disconnect()

    return messages


def normalize_number(number):
    """Normalize a phone number to digits only with leading +1 if needed."""
    digits = "".join(c for c in number if c.isdigit() or c == "+")
    if not digits.startswith("+"):
        if len(digits) == 10:
            digits = "+1" + digits
        elif len(digits) == 11 and digits.startswith("1"):
            digits = "+" + digits
    return digits

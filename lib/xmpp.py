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
        if is_jid(to_number):
            dest_jid = to_number
        else:
            dest_jid = normalize_number(to_number) + "@cheogram.com"
        client.send_message(mto=dest_jid, mbody=message, mtype="chat")
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


async def list_contacts(jid, password):
    """List all contacts in the XMPP roster."""
    client = SMSClient(jid, password)
    contacts = []
    done = asyncio.get_event_loop().create_future()

    async def on_session_start(event):
        try:
            client.send_presence()
            await client.get_roster()
            for rjid in client.client_roster:
                if rjid == jid:
                    continue
                item = client.client_roster[rjid]
                contacts.append({
                    "jid": rjid,
                    "name": item["name"] or "",
                    "subscription": item["subscription"],
                })
        except Exception as e:
            log.error("Failed to list contacts: %s", e)
        finally:
            done.set_result(True)

    client.add_event_handler("session_start", on_session_start)

    client.connect()

    try:
        await asyncio.wait_for(done, timeout=10)
    except asyncio.TimeoutError:
        log.error("Timed out listing contacts")
    finally:
        client.disconnect()

    return contacts


async def add_contact(jid, password, contact_jid):
    """Add a contact to the XMPP roster and subscribe to their presence."""
    client = SMSClient(jid, password)
    done = asyncio.get_event_loop().create_future()

    async def on_session_start(event):
        try:
            client.send_presence()
            await client.get_roster()
            client.send_presence(pto=contact_jid, ptype="subscribe")
            await asyncio.sleep(1)
            done.set_result(True)
        except Exception as e:
            log.error("Failed to add contact: %s", e)
            done.set_result(False)

    client.add_event_handler("session_start", on_session_start)

    client.connect()

    try:
        result = await asyncio.wait_for(done, timeout=10)
    except asyncio.TimeoutError:
        result = False
    finally:
        client.disconnect()

    return result


async def listen_messages(jid, password, callback, timeout=60):
    """Connect and listen for incoming messages in real-time."""
    client = SMSClient(jid, password)

    def on_message(msg):
        if msg["type"] in ("chat", "normal") and msg["body"]:
            callback({
                "from": str(msg["from"]),
                "to": str(msg["to"]),
                "body": str(msg["body"]),
            })

    client.add_event_handler("message", on_message)

    async def on_session_start(event):
        client.send_presence()
        await client.get_roster()
        print(f"Listening ({timeout}s)..." if timeout else "Listening...", flush=True)

    client.add_event_handler("session_start", on_session_start)

    client.connect()

    try:
        if timeout:
            await asyncio.sleep(timeout)
        else:
            await asyncio.Future()  # block forever
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        client.disconnect()


def is_jid(value):
    """Check if a value looks like an XMPP JID rather than a phone number."""
    return any(c.isalpha() for c in value)


def normalize_number(number):
    """Normalize a phone number to digits only with leading +1 if needed."""
    digits = "".join(c for c in number if c.isdigit() or c == "+")
    if not digits.startswith("+"):
        if len(digits) == 10:
            digits = "+1" + digits
        elif len(digits) == 11 and digits.startswith("1"):
            digits = "+" + digits
    return digits

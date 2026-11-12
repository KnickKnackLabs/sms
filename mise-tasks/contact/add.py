#!/usr/bin/env -S uv run --locked python
#
# MISE description="Add a contact to the XMPP roster"
# MISE dir="{{config_root}}"
#
# USAGE arg "<jid>" help="Jabber ID to add (e.g. user@server.com)"
# USAGE example "sms contact add friend@example.com" header="Add an XMPP contact"

import asyncio
import os
import sys

from duration import SECOND
from slixmpp import JID
from sms import wait_ready
from sms.contacts import add_contact
from xmpp import SMSClient


async def main() -> None:
    client = SMSClient(
        os.environ["SMS_JID"],
        os.environ["SMS_PASSWORD"],
    )

    ready = wait_ready(client)

    try:
        # Connect
        async with asyncio.timeout(3 * SECOND):
            _ = await client.connect()
            await ready

        # Add contact
        async with asyncio.timeout(5 * SECOND):
            contact = await add_contact(
                client,
                JID(os.environ["usage_jid"]),
            )

            print(contact)

    except TimeoutError:
        print("Timed out", file=sys.stderr)
        sys.exit(1)

    except PermissionError as error:
        print(error, file=sys.stderr)
        sys.exit(1)

    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())

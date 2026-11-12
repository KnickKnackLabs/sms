#!/usr/bin/env -S uv run --locked python
#
# MISE description="List contacts in the XMPP roster"
# MISE dir="{{config_root}}"
#
# USAGE example "sms contact list"

import asyncio
import os
import sys

from duration import SECOND
from sms import wait_ready
from sms.contacts import list_contacts
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

        # List contacts
        async with asyncio.timeout(5 * SECOND):
            contacts = await list_contacts(client)

            for contact in contacts:
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

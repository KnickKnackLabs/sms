#!/usr/bin/env -S uv run --locked python
#
# MISE description="Send an SMS message"
# MISE dir="{{config_root}}"
#
# USAGE arg "<to>" help="Recipient XMPP JID"
# USAGE arg "<body>" help="Message text to send"
#
# USAGE example "sms message send +15551234567@cheogram.com 'Hello'" header="Send one SMS message"
# USAGE example "sms message send person@example.com 'Hello'" header="Send one message"

import asyncio
import os
import sys

from duration import SECOND
from slixmpp import JID
from sms import wait_ready
from sms.messages import send_message
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
            to = JID(os.environ["usage_to"])
            body = os.environ["usage_body"]

            await send_message(client, to, body)
            print(f"Queued SMS to {to}")

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

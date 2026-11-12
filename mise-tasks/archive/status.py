#!/usr/bin/env -S uv run --locked python
#
# MISE description="Check MAM (Message Archive Management) status"
# MISE dir="{{config_root}}"
#
# USAGE example "sms archive status"

import asyncio
import os
import sys

from duration import SECOND
from sms import wait_ready
from sms.archive import archive_status
from xmpp import XEP_0313, XEP_0441, SMSClient


async def main():
    client = SMSClient(
        os.environ["SMS_JID"],
        os.environ["SMS_PASSWORD"],
    )

    for xep in [XEP_0313, XEP_0441]:
        client.register_plugin(xep)

    ready = wait_ready(client)

    try:
        # Connect
        async with asyncio.timeout(3 * SECOND):
            _ = await client.connect()
            await ready

        # Check archive status
        async with asyncio.timeout(5 * SECOND):
            status = await archive_status(client)
            print(status)

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

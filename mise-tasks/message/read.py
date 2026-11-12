#!/usr/bin/env -S uv run --locked python
#
# MISE description="Read recent SMS messages"
# MISE dir="{{config_root}}"
#
# USAGE flag "--limit <limit>" default="20" help="Maximum number of messages to retrieve"
# USAGE flag "--json" default=#false help="Output as JSON"

# USAGE example "sms message read --limit 10 --json" header="Read ten recent messages as JSON"

import asyncio
import json
import os
import sys

from duration import SECOND
from sms import wait_ready
from sms.messages import Message as SMSMessage, list_messages
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
            limit = int(os.environ["usage_limit"])
            as_json = os.environ["usage_json"] == "true"

            messages = await list_messages(client, limit)

            if as_json:
                print(
                    json.dumps(
                        list(map(SMSMessage.to_dict, messages)),
                        indent=2,
                    )
                )

            else:
                for msg in messages:
                    print(msg)
                    print()

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

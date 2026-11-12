#!/usr/bin/env -S uv run --locked python
#
# MISE description="Listen for incoming messages in real-time"
# MISE dir="{{config_root}}"
#
# USAGE flag "--timeout <timeout>" required=#false help="Listen at most <timeout> seconds"
# USAGE flag "--json" default=#false help="Output each message as one JSON object (JSON Lines)"
# USAGE flag "--once" default=#false help="Return after one message"
# USAGE flag "-s --silent" default=#false help="Silent mode"
#
# USAGE example "sms message listen" header="Keep listening for incoming messages"
# USAGE example "sms message listen --timeout 30 --json" header="Stream incoming messages as JSON Lines for 30 seconds"
# USAGE example "sms message listen --once" header="Wait for the next incoming message, then exit"
# USAGE example "sms message listen --once --timeout 30" header="Wait up to 30 seconds for an incoming message"
# USAGE example "sms message listen --once --json" header="Print the next message as JSON, then exit"
# USAGE example "sms message listen --once -s" header="Wait silently for a message"

import asyncio
import json
import os
import sys
from contextlib import aclosing

from duration import SECOND
from sms import wait_ready
from sms.messages import listen_for_messages
from xmpp import SMSClient


def positive_int_or_none(value: str | None) -> int | None:
    if value is None:
        return None

    number = int(value)

    if number <= 0:
        raise ValueError("positive number required")

    return number


async def main():
    client = SMSClient(
        os.environ["SMS_JID"],
        os.environ["SMS_PASSWORD"],
    )

    once = os.environ["usage_once"] == "true"
    silent = os.environ["usage_silent"] == "true"
    as_json = os.environ["usage_json"] == "true"

    try:
        timeout = positive_int_or_none(os.environ.get("usage_timeout"))

    except ValueError:
        print("--timeout must be a positive integer", file=sys.stderr)
        sys.exit(2)

    if isinstance(timeout, int):
        timeout *= SECOND

    ready = wait_ready(client)

    try:
        # Connect
        try:
            async with asyncio.timeout(3 * SECOND):
                _ = await client.connect()
                await ready

        except TimeoutError:
            print("Connection timed out", file=sys.stderr)
            sys.exit(1)

        except PermissionError as error:
            print(error, file=sys.stderr)
            sys.exit(1)

        # Listen to messages
        try:
            async with asyncio.timeout(timeout):
                async with aclosing(listen_for_messages(client)) as messages:
                    async for msg in messages:
                        if not silent:
                            if as_json:
                                print(json.dumps(msg.to_dict()), flush=True)

                            else:
                                print(msg)
                                print()

                        if once:
                            break

        except TimeoutError:
            if once:
                sys.exit(124)

        except ConnectionError as error:
            print(error, file=sys.stderr)
            sys.exit(1)

    finally:
        await client.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        sys.exit(130)

#!/usr/bin/env -S uv run --locked python
# MISE description="Send an SMS message"
# MISE dir="{{config_root}}"
# USAGE arg "<destination>" help="Phone number (e.g. +19195551234) or XMPP JID (e.g. user@server.com)"
# USAGE arg "<message>" help="Message text to send"
# USAGE example "mise run send +15551234567 'Hello'" header="Send one SMS message"

import asyncio
import os
import sys

sys.path.insert(0, os.environ["MISE_CONFIG_ROOT"] + "/lib")
from xmpp import is_jid, normalize_number, send_sms


def main():
    jid = os.environ.get("SMS_JID", "")
    password = os.environ.get("SMS_PASSWORD", "")

    if not jid or not password:
        print("SMS_JID and SMS_PASSWORD must be set")
        sys.exit(1)

    destination = os.environ["usage_destination"]
    message = os.environ["usage_message"]

    ok = asyncio.run(send_sms(jid, password, destination, message))

    if ok:
        if is_jid(destination):
            print(f"Sent to {destination}")
        else:
            print(f"Sent to {normalize_number(destination)}")
    else:
        print("Failed to send message")
        sys.exit(1)


if __name__ == "__main__":
    main()

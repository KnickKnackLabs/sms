<div align="center">

# sms

**SMS tools**

Send and receive SMS through [JMP.chat](https://jmp.chat) using an XMPP account.

![tests: 5](https://img.shields.io/badge/tests-5-blue?style=flat)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue?style=flat)](LICENSE)

</div>

## Install

Start with an XMPP account linked to a JMP.chat number. Follow [JMP.chat's setup instructions](https://jmp.chat) to activate the account, then provide its XMPP credentials:

```bash
shiv install sms

export SMS_JID="agent@xmpp.chat"
export SMS_PASSWORD="..."

sms status  # Check connection and authentication
```

Keep credentials outside the repository. For message history, enable archiving:

```bash
sms archive enable
sms archive status
```

## Run

```bash
# Send through the gateway using the recipient's full XMPP JID
sms message send +15551234567@cheogram.com "Hello from the terminal"

# Read the ten most recent archived messages
sms message read --limit 10

# Wait up to five minutes for one incoming message, then return JSON
sms message listen --once --timeout 300 --json

# Or stream incoming messages as JSON Lines until interrupted
sms message listen --json
```

<details>
<summary><b>Notes</b></summary>

- **Addressing.** Sending takes a full XMPP JID, such as `+15551234567@cheogram.com`
- **Contacts.** Some servers filter messages from unlisted senders. Add a phone JID to the roster with `sms contact add +15551234567@cheogram.com`
- **History.** Archive reading uses the server's [MAM archive](https://xmpp.org/extensions/xep-0313.html). Don't forget to enable archiving, if you need it.
- **Delivery.** The send command confirms queuing, rather than carrier delivery.

</details>

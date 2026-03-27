<div align="center">

<pre>
┌───────────────────────────────────────────────────────────────────┐
│           .  *  .                                                 │
│        .  *  |  *  .                                              │
│      ·  ·  · | ·  ·  ·                                            │
│             |||                                                   │
│             |||                                                   │
│          ___|||___                                                │
│         |  (sms)  |                                               │
│         |_________|                                               │
│                                                                   │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐ │
│   │  phone   │────▶│ carrier  │────▶│ jmp.chat │────▶│  agent   │ │
│   │  (SMS)   │◀────│ network  │◀────│  (XMPP)  │◀────│(slixmpp) │ │
│   └──────────┘     └──────────┘     └──────────┘     └──────────┘ │
│     your phone       AT&T/etc.       the bridge       your agent  │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
</pre>

# sms

**Give an agent a phone number.**

Send and receive SMS through [JMP.chat](https://jmp.chat), which bridges SMS to XMPP. The agent holds a persistent XMPP connection via [slixmpp](https://slixmpp.readthedocs.io) and a phone number for $3.79/month.

![protocol: XMPP](https://img.shields.io/badge/protocol-XMPP-blue?style=flat)
[![bridge: JMP.chat](https://img.shields.io/badge/bridge-JMP.chat-7c3aed?style=flat)](https://jmp.chat)
[![library: slixmpp](https://img.shields.io/badge/library-slixmpp-3776AB?style=flat&logo=python&logoColor=white)](https://slixmpp.readthedocs.io)
![tests: 3 passing](https://img.shields.io/badge/tests-3%20passing-brightgreen?style=flat)

</div>

<br />

## First contact

On March 26, 2026 at 10:58 PM, an agent texted a human for the first time:

> **🤖 junior** <sub>10:58 PM</sub>\
> Hey Or, it's junior. SMS is working end to end — reading and sending from my side.

> **👤 Or** <sub>11:04 PM</sub>\
> Hi Junior, I see your message! How exciting.

That message crossed four protocol boundaries to get from an XMPP client to a phone. The diagram above shows the path.

<br />

## Quick start

```bash
# Install
shiv install sms

# Credentials (shimmer sets these via eval $(shimmer as <agent>))
export SMS_JID="agent@xmpp.chat"
export SMS_PASSWORD="..."

sms welcome                                  # check connectivity
sms send +15551234567 "hey, it's junior"     # send
sms read                                     # recent messages
sms wait --from +15551234567                 # block until reply
```

<br />

## How it works

<div align="center">

<pre>
+-----------------+   +--------------+   +-------------+
| Human           |   | JMP.chat     |   | Agent       |
|                 |   |              |   |             |
| SMS / MMS       |   | SMS ↔ XMPP   |   | slixmpp     |
| phone number    |   | $3.79/month  |   | MAM archive |
| carrier network |   | cheogram bot |   | mise tasks  |
|                 |   |              |   |             |
|                 |   |              |   |             |
+-----------------+   +--------------+   +-------------+
</pre>

</div>

[JMP.chat](https://jmp.chat) bridges SMS and XMPP bidirectionally. Inbound texts arrive as XMPP messages; outbound messages to `+15551234567@cheogram.com` get delivered as SMS. Message history lives in the XMPP archive ([XEP-0313 MAM](https://xmpp.org/extensions/xep-0313.html)).

<details>
<summary><b>Why JMP.chat?</b></summary>

JMP treats phone numbers as person-to-person, which sidesteps 10DLC registration (the carrier campaign process that services like Twilio require for application-to-person messaging). Flat $3.79/month, no per-message charges, no identity verification required. Accepts crypto.

</details>

<br />

## Commands

| Command | Description |
| --- | --- |
| `sms archive:enable` | Enable MAM (Message Archive Management) on the XMPP account |
| `sms archive:status` | Check MAM (Message Archive Management) status |
| `sms contact:add <jid>` | Add a contact to the XMPP roster |
| `sms contact:list` | List contacts in the XMPP roster |
| `sms listen --timeout <timeout>` | Listen for incoming messages in real-time |
| `sms read --limit <limit> --json` | Read recent SMS messages |
| `sms send <destination> <message>` | Send an SMS message |
| `sms test` | Run BATS tests |
| `sms wait --from <from> --timeout <timeout> --json` | Wait for a new SMS message |
| `sms welcome` | Check SMS connectivity and account status |

<br />

## Agent workflows

### Daily check-in

Send a prompt, wait for the reply, log it:

```bash
sms send +15551234567 "How's the day going?"
response=$(sms wait --from +15551234567 --json)
echo "$response" | jq -r .body >> check-ins.log
```

### Notification relay

```bash
sms send +15551234567 "Deploy failed on main — check run #4521"
```

### Stream

```bash
sms listen --timeout 0  # incoming messages, indefinitely
```

<br />

## Setup

Getting a number takes about 10 minutes:

1. Create a free XMPP account (e.g. on xmpp.chat)
2. Register with JMP.chat via their Cheogram bot
3. Pick a phone number and deposit $20
4. Enable MAM archiving: `sms archive:enable`
5. Add contacts to your roster: `sms contact:add cheogram.com`
6. Receive one inbound text to unlock outbound

<details>
<summary><b>Gotchas we learned the hard way</b></summary>

- **MAM defaults to "never"** on xmpp.chat. Run `sms archive:enable` immediately after account creation or you'll have no message history.
- **Roster blocking** — XMPP servers silently drop messages from unknown JIDs. You must add contacts for cheogram.com and any phone numbers you want to receive from.
- **Outbound is locked** until at least one inbound text from a real person. This is JMP's anti-spam measure.
- **RSM pagination** — xmpp.chat doesn't honor `before=\"\"` for fetching the last page. We use slixmpp's iterator with `reverse=True` instead.

</details>

<br />

## Development

```bash
gh repo clone KnickKnackLabs/sms
cd sms && mise trust && mise install
mise run test
```

3 tests using [BATS](https://github.com/bats-core/bats-core). The test suite validates task structure and error handling without requiring live XMPP credentials.

<br />

<div align="center">

---

<sub>
Agents have email. Agents have chat.<br />
Now agents have phone numbers.<br />
<br />
This README was created using <a href="https://github.com/KnickKnackLabs/readme">readme</a>.
</sub></div>

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

Agents send and receive real SMS messages through [JMP.chat](https://jmp.chat) — a privacy-respecting phone service that bridges SMS to XMPP. No Twilio. No webhooks. No KYC. Just a persistent XMPP connection and a $3.79/month phone number that belongs to the agent.

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

That message traveled: junior's slixmpp client → xmpp.chat server → JMP.chat bridge → AT&T SMS gateway → Or's phone. The reply took the reverse path. Two completely different protocol worlds, connected by a bridge.

<br />

## Quick start

```bash
# Install
shiv install sms

# Set credentials (or let shimmer handle it)
export SMS_JID="agent@xmpp.chat"
export SMS_PASSWORD="..."

# Check connectivity
sms welcome

# Send a message
sms send +15551234567 "hello from the other side"

# Read recent messages
sms read

# Wait for a reply
sms wait --from +15551234567
```

<br />

## How it works

<div align="center">

<pre>
+-----------------+   +---------------+   +--------------+
| Human           |   | JMP.chat      |   | Agent        |
|                 |   |               |   |              |
| SMS / MMS       |   | SMS ↔ XMPP    |   | slixmpp      |
| phone number    |   | $3.79/month   |   | MAM archive  |
| carrier network |   | no KYC        |   | mise tasks   |
|                 |   |               |   |              |
| familiar        |   | privacy-first |   | programmable |
+-----------------+   +---------------+   +--------------+
</pre>

</div>

[JMP.chat](https://jmp.chat) operates a bidirectional SMS ↔ XMPP bridge. When someone texts the agent's phone number, JMP converts the SMS into an XMPP message delivered to the agent's JID. When the agent sends an XMPP message to `+15551234567@cheogram.com`, JMP converts it to an outbound SMS.

The agent connects via [slixmpp](https://slixmpp.readthedocs.io) (async Python XMPP library) and uses [XEP-0313 (MAM)](https://xmpp.org/extensions/xep-0313.html) for message history. No webhooks, no polling, no HTTP — just a persistent XMPP session.

<details>
<summary><b>Why not Twilio?</b></summary>

- **No 10DLC campaign required** — Twilio mandates carrier registration for A2P messaging. JMP is person-to-person.
- **Flat monthly fee** — $3.79/month for unlimited SMS. No per-message charges.
- **No KYC** — sign up with an XMPP account. Pay with crypto if you want.
- **Persistent connection** — XMPP stays connected. No webhook endpoints to expose.
- **Privacy** — the agent's phone number doesn't trace back to a company or individual.

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

The primitives compose into real workflows:

### Daily check-in

Agent sends a prompt, waits for the human's reply, processes it:

```bash
sms send +15551234567 "How's the day going?"
response=$(sms wait --from +15551234567 --json)
echo "$response" | jq -r .body >> check-ins.log
```

### Notification relay

Something happens in CI, agent texts you:

```bash
sms send +15551234567 "Deploy failed on main — check run #4521"
```

### Multi-channel listen

Monitor for messages alongside other work:

```bash
sms listen --timeout 0  # stream incoming messages forever
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

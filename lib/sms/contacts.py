from dataclasses import dataclass
from typing import cast, override

from slixmpp import JID
from slixmpp.roster import RosterItem
from xmpp import SMSClient


@dataclass(frozen=True)
class Contact:
    jid: str
    name: str
    subscription: str

    @override
    def __str__(self) -> str:
        label = self.jid

        if self.name:
            label += f" ({self.name})"

        return f"{label} [{self.subscription}]"


def to_contact(jid: str, item: RosterItem) -> Contact:
    return Contact(
        jid=jid,
        name=cast(str, item["name"] or ""),
        subscription=cast(str, item["subscription"]),
    )


async def list_contacts(client: SMSClient) -> list[Contact]:
    _ = await client.get_roster()

    roster = client.client_roster

    contact_jids = filter(
        lambda jid: jid != client.boundjid.bare,
        roster,
    )

    contacts = map(  # noqa: C417
        lambda jid: to_contact(jid, roster[jid]),
        contact_jids,
    )

    return list(contacts)


async def add_contact(client: SMSClient, contact_jid: JID) -> Contact:
    _ = await client.get_roster()

    request = client.update_roster(contact_jid)

    if request is None:
        raise RuntimeError("Roster update did not create a request")

    _ = await request
    _ = await client.get_roster()

    address = contact_jid.bare

    return to_contact(
        address,
        client.client_roster[address],
    )

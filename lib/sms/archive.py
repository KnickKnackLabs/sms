import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, cast, override

from slixmpp import JID, Iq
from slixmpp.plugins.xep_0313.stanza import End, Metadata, Start
from slixmpp.types import MAMDefault
from xmpp import XEP_0313, XEP_0441, SMSClient


@dataclass(frozen=True)
class ArchiveStatus:
    default_policy: MAMDefault
    oldest: datetime | None = None
    newest: datetime | None = None

    @override
    def __str__(self) -> str:
        lines = [f"Archiving: {self.default_policy}"]

        if self.oldest is not None:
            lines.append(f"Oldest: {self.oldest.isoformat()}")

        if self.newest is not None:
            lines.append(f"Newest: {self.newest.isoformat()}")

        if self.oldest is None and self.newest is None:
            lines.append("Archive: empty")

        return "\n".join(lines)


async def enable_preferences(client: SMSClient) -> MAMDefault:
    preferences = cast(ArchivePreferences, client.plugin[XEP_0441])

    current, always, never = await preferences.get_preferences()

    _ = await preferences.set_preferences(
        default="always",
        always=always,
        never=never,
    )

    return current


async def archive_status(client: SMSClient) -> ArchiveStatus:
    preferences, archive = (
        cast(ArchivePreferences, client.plugin[XEP_0441]),
        cast(ArchiveMetadata, client.plugin[XEP_0313]),
    )

    default_policy, _, _ = await preferences.get_preferences()

    # Check archive metadata
    response = await archive.get_archive_metadata()

    metadata = response.get_plugin("mam_metadata", check=True)

    if not isinstance(metadata, Metadata):
        raise TypeError("Server response did not include archive metadata")

    start = metadata.get_plugin("start", check=True)
    end = metadata.get_plugin("end", check=True)

    return ArchiveStatus(
        default_policy=default_policy,
        oldest=timestamp_or_none(start),
        newest=timestamp_or_none(end),
    )


class ArchiveMetadata(Protocol):
    def get_archive_metadata(self) -> asyncio.Future[Iq]: ...


class ArchivePreferences(Protocol):
    async def get_preferences(
        self,
    ) -> tuple[MAMDefault, list[JID], list[JID]]: ...

    def set_preferences(
        self,
        *,
        default: MAMDefault,
        always: list[JID],
        never: list[JID],
    ) -> asyncio.Future[Iq]: ...


def timestamp_or_none(v: object) -> datetime | None:
    if isinstance(v, Start):
        return v.get_timestamp()

    if isinstance(v, End):
        return v.get_timestamp()

    return None

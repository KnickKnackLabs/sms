from asyncio import Future
from types import ModuleType
from typing import override

from slixmpp.basexmpp import BaseXMPP
from slixmpp.jid import JID
from slixmpp.roster.single import RosterNode
from slixmpp.stanza import Iq

class ClientXMPP(BaseXMPP):
    client_roster: RosterNode

    # fmt: off

    def __init__(
        self,
        jid: str | JID,
        password: str,
    ) -> None: ...

    @override
    def connect(
        self,
        host: str | None = ...,
        port: int | None = ...,
    ) -> Future[object]: ...

    @override
    def disconnect(
        self,
        wait: float = ...,
        reason: str | None = ...,
        ignore_send_queue: bool = ...,
    ) -> Future[None]: ...

    @override
    def register_plugin(
        self,
        plugin: str,
        pconfig: dict[str, object] | None = ...,
        module: str | ModuleType | None = ...,
    ) -> None: ...

    def get_roster(self) -> Future[Iq | None]: ...
    def update_roster(self, jid: JID) -> Future[Iq] | None: ...

    # fmt: on

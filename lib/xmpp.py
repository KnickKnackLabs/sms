"""Shared XMPP client logic for jmp.chat SMS integration."""

from collections.abc import Awaitable, Callable
from enum import StrEnum

import slixmpp

XEP_0030 = "xep_0030"  # Service Discovery
XEP_0313 = "xep_0313"  # Archive (MAM)
XEP_0441 = "xep_0441"  # Preferences


class XMPPEvent(StrEnum):
    SESSION_START = "session_start"
    FAILED_AUTH = "failed_auth"
    MESSAGE = "message"
    DISCONNECTED = "disconnected"


class SMSClient(slixmpp.ClientXMPP):
    """XMPP client for sending and receiving SMS via jmp.chat."""

    def __init__(self, jid: str, password: str) -> None:
        super().__init__(jid, password)
        self.register_plugin(XEP_0030)  # Service Discovery
        self.register_plugin(XEP_0313)  # Message Archive Management (MAM)

    async def connect_and_run[T](
        self,
        callback: Callable[["SMSClient"], Awaitable[T]],
    ) -> T:
        """Connect, run a callback, then disconnect."""
        _ = self.connect()

        try:
            result = await callback(self)

        finally:
            _ = await self.disconnect()

        return result


def is_jid(value: str) -> bool:
    """Check if a value looks like an XMPP JID rather than a phone number."""
    return any(c.isalpha() for c in value)


def normalize_number(number: str) -> str:
    """Normalize a phone number to digits only with leading +1 if needed."""
    digits = "".join(c for c in number if c.isdigit() or c == "+")

    if not digits.startswith("+"):
        if len(digits) == 10:
            digits = "+1" + digits

        elif len(digits) == 11 and digits.startswith("1"):
            digits = "+" + digits

    return digits

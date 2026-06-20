"""Output formatting helpers for sms tasks."""

import json
from datetime import datetime, timezone


def utc_timestamp():
    """Return the current UTC timestamp for live message events."""
    return datetime.now(timezone.utc).isoformat()


def listen_event(message, timestamp=None):
    """Normalize a live listen message into a serializable event."""
    event = {
        "from": str(message["from"]),
        "to": str(message["to"]),
        "body": str(message["body"]),
    }
    if timestamp is not None:
        event["timestamp"] = timestamp
    return event


def format_listen_human(event):
    """Format a listen event for human-readable terminal output."""
    ts = event.get("timestamp", "")
    prefix = f"[{ts}] " if ts else ""
    return f"{prefix}{event['from']}\n  {event['body']}\n"


def format_json_line(event):
    """Format one event as one JSON Lines record."""
    return json.dumps(event, ensure_ascii=False)

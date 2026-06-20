#!/usr/bin/env python3
"""Tests for listen output formatting helpers."""

import json
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo / "lib"))

from output import format_json_line, format_listen_human, listen_event


def test_json_line_preserves_multiline_body():
    event = listen_event(
        {
            "from": "+15551234567@cheogram.com",
            "to": "agent@xmpp.chat",
            "body": "Hi Quick!\n\nParent situation:\nMy kid refuses the shower.",
        },
        timestamp="2026-06-20T17:34:54+00:00",
    )
    line = format_json_line(event)
    parsed = json.loads(line)

    assert parsed == {
        "from": "+15551234567@cheogram.com",
        "to": "agent@xmpp.chat",
        "body": "Hi Quick!\n\nParent situation:\nMy kid refuses the shower.",
        "timestamp": "2026-06-20T17:34:54+00:00",
    }
    assert "\n" not in line


def test_human_output_matches_legacy_shape_without_timestamp():
    event = listen_event(
        {
            "from": "+15551234567@cheogram.com",
            "to": "agent@xmpp.chat",
            "body": "hello",
        }
    )

    assert format_listen_human(event) == "+15551234567@cheogram.com\n  hello\n"


if __name__ == "__main__":
    test_json_line_preserves_multiline_body()
    test_human_output_matches_legacy_shape_without_timestamp()
    print("listen output tests passed")

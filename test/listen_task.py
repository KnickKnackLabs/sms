#!/usr/bin/env python3
"""Tests for the listen task wrapper without a live XMPP connection."""

import contextlib
import io
import json
import os
import runpy
import sys
import types
from pathlib import Path

repo = Path(__file__).resolve().parents[1]
task_path = repo / ".mise" / "tasks" / "listen"


async def fake_listen_messages(jid, password, callback, timeout=60, announce=True):
    if announce:
        print(f"Listening ({timeout}s)..." if timeout else "Listening...")
    callback(
        {
            "from": "+15551234567@cheogram.com",
            "to": "agent@xmpp.chat",
            "body": "hello\nsecond line",
        }
    )


def run_listen_task(*, as_json: bool) -> str:
    fake_xmpp = types.ModuleType("xmpp")
    fake_xmpp.listen_messages = fake_listen_messages

    old_env = os.environ.copy()
    old_xmpp = sys.modules.get("xmpp")
    old_argv = sys.argv[:]
    output = io.StringIO()
    try:
        os.environ.update(
            {
                "MISE_CONFIG_ROOT": str(repo),
                "SMS_JID": "agent@xmpp.chat",
                "SMS_PASSWORD": "fake-password",
                "usage_timeout": "0",
                "usage_json": "true" if as_json else "false",
            }
        )
        sys.modules["xmpp"] = fake_xmpp
        sys.argv = [str(task_path)]
        with contextlib.redirect_stdout(output):
            runpy.run_path(str(task_path), run_name="__sms_listen_task_test__")
        return output.getvalue()
    finally:
        os.environ.clear()
        os.environ.update(old_env)
        sys.argv = old_argv
        if old_xmpp is None:
            sys.modules.pop("xmpp", None)
        else:
            sys.modules["xmpp"] = old_xmpp


def test_json_mode_stdout_is_json_lines_only():
    output = run_listen_task(as_json=True)
    lines = output.splitlines()

    assert len(lines) == 1
    assert "Listening" not in output
    event = json.loads(lines[0])
    assert event["from"] == "+15551234567@cheogram.com"
    assert event["body"] == "hello\nsecond line"


def test_human_mode_keeps_startup_banner():
    output = run_listen_task(as_json=False)

    assert output.startswith("Listening...\n")
    assert "+15551234567@cheogram.com\n  hello\nsecond line\n" in output


if __name__ == "__main__":
    test_json_mode_stdout_is_json_lines_only()
    test_human_mode_keeps_startup_banner()
    print("listen task tests passed")

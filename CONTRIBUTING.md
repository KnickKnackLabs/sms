# Contributing

`sms` gives agents an SMS-capable XMPP client through JMP.chat. Keep infrastructure changes boring and preserve the live-network boundary: tests and CI must not require real SMS credentials or external XMPP accounts unless a task explicitly documents that it is an integration test.

## Structure

```text
sms/
├── mise.toml              # tools, settings, and codebase lint config
├── README.tsx             # source for generated README.md
├── README.md              # generated; keep in sync with README.tsx
├── CONTRIBUTING.md        # repo orientation surface
├── lib/xmpp.py            # shared async XMPP/SMS client logic
├── .mise/tasks/           # user-facing sms commands
└── test/                  # BATS tests and helpers
```

## Local setup

```bash
mise trust
mise install
mise run test
```

For live SMS checks, set credentials in the environment first:

```bash
export SMS_JID="agent@xmpp.chat"
export SMS_PASSWORD="..."
mise run welcome
```

Do not commit credentials, phone-number routing changes, payment setup, or account-provisioning side effects.

## Task conventions

- Use mise file tasks with `#MISE description`.
- Use `#USAGE` for task arguments and flags.
- Give optional `#USAGE` values explicit defaults so stale inherited `usage_*` environment cannot change behavior.
- Keep network/XMPP logic in `lib/xmpp.py`; task files should stay thin CLI wrappers.
- Python task files may use `uv run --script` with PEP 723 dependencies; shared imports should go through `MISE_CONFIG_ROOT/lib`.

## Test conventions

- BATS tests should call tasks through `mise run`, via `test/test_helper.bash`.
- The default test suite must not need live XMPP credentials.
- Prefer pure helper tests or mocked boundaries for behavior that does not need a real server.
- Use a separate, explicit integration-test path before adding local XMPP server coverage.

## README workflow

Edit `README.tsx`, then regenerate and check the output:

```bash
readme build
readme build --check
```

CI also checks that `README.md` matches `README.tsx`.

## Validation before merge

```bash
mise run test
codebase lint "$PWD"
readme build --check
git diff --check
```

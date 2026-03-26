# Tests must be run via `mise run test`
if [ -z "${MISE_CONFIG_ROOT:-}" ]; then
  echo "MISE_CONFIG_ROOT not set — run tests via: mise run test" >&2
  exit 1
fi

sms() {
  local subcmd="$1"; shift
  cd "$MISE_CONFIG_ROOT" && mise run "$subcmd" -- "$@"
}
export -f sms

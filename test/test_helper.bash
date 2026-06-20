# Shared fixtures for sms tests.

# Run a repo task through mise so tests exercise the real task path.
sms() {
  cd "$REPO_DIR" && mise run -q "$@"
}
export -f sms

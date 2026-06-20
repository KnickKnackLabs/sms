#!/usr/bin/env bats

setup() {
  load test_helper
}

@test "welcome: fails without credentials" {
  unset SMS_JID SMS_PASSWORD
  run sms welcome
  [ "$status" -ne 0 ]
  [[ "$output" == *"SMS_JID and SMS_PASSWORD must be set"* ]]
}

@test "send: fails without credentials" {
  unset SMS_JID SMS_PASSWORD
  run sms send "+19195551234" "test"
  [ "$status" -ne 0 ]
  [[ "$output" == *"SMS_JID and SMS_PASSWORD must be set"* ]]
}

@test "read: fails without credentials" {
  unset SMS_JID SMS_PASSWORD
  run sms read
  [ "$status" -ne 0 ]
  [[ "$output" == *"SMS_JID and SMS_PASSWORD must be set"* ]]
}

@test "wait: fails without credentials" {
  unset SMS_JID SMS_PASSWORD
  run sms wait
  [ "$status" -ne 0 ]
  [[ "$output" == *"SMS_JID and SMS_PASSWORD must be set"* ]]
}

@test "listen: fails without credentials" {
  unset SMS_JID SMS_PASSWORD
  run sms listen
  [ "$status" -ne 0 ]
  [[ "$output" == *"SMS_JID and SMS_PASSWORD must be set"* ]]
}

@test "listen: JSON Lines formatting preserves multiline bodies" {
  run python3 "$REPO_DIR/test/listen_output.py"
  [ "$status" -eq 0 ]
  [[ "$output" == *"listen output tests passed"* ]]
}

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
  run sms send -- "+19195551234" "test"
  [ "$status" -ne 0 ]
  [[ "$output" == *"SMS_JID and SMS_PASSWORD must be set"* ]]
}

@test "read: fails without credentials" {
  unset SMS_JID SMS_PASSWORD
  run sms read
  [ "$status" -ne 0 ]
  [[ "$output" == *"SMS_JID and SMS_PASSWORD must be set"* ]]
}

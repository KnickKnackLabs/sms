#!/usr/bin/env bats

setup() {
  load test_helper
  unset SMS_JID SMS_PASSWORD
}

@test "welcome: fails without credentials" {
  run sms welcome
  [[ "${status}" -ne 0 ]]
  [[ "${output}" == *"SMS_JID and SMS_PASSWORD must be set"* ]]
}

@test "send: fails without credentials" {
  run sms send "+19195551234" "test"
  [[ "${status}" -ne 0 ]]
  [[ "${output}" == *"SMS_JID and SMS_PASSWORD must be set"* ]]
}

@test "read: fails without credentials" {
  run sms message:read
  [[ "${status}" -ne 0 ]]
  [[ "${output}" == *"SMS_JID and SMS_PASSWORD must be set"* ]]
}

@test "wait: fails without credentials" {
  run sms wait
  [[ "${status}" -ne 0 ]]
  [[ "${output}" == *"SMS_JID and SMS_PASSWORD must be set"* ]]
}

@test "listen: fails without credentials" {
  run sms listen
  [[ "${status}" -ne 0 ]]
  [[ "${output}" == *"SMS_JID and SMS_PASSWORD must be set"* ]]
}

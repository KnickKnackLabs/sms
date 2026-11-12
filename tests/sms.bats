#!/usr/bin/env bats

setup() {
  load test_helper
  unset SMS_JID SMS_PASSWORD
}

@test "status: fails without credentials" {
  run sms status
  [[ "${status}" -ne 0 ]]
  [[ "${output}" == *"KeyError: 'SMS_JID'"* ]]
}

@test "message:send: fails without credentials" {
  run sms message:send "+15551234567@cheogram.com" "test"
  [[ "${status}" -ne 0 ]]
  [[ "${output}" == *"KeyError: 'SMS_JID'"* ]]
}

@test "message:read: fails without credentials" {
  run sms message:read
  [[ "${status}" -ne 0 ]]
  [[ "${output}" == *"KeyError: 'SMS_JID'"* ]]
}

@test "message:listen once: fails without credentials" {
  run sms message:listen --once
  [[ "${status}" -ne 0 ]]
  [[ "${output}" == *"KeyError: 'SMS_JID'"* ]]
}

@test "message:listen: fails without credentials" {
  run sms message:listen
  [[ "${status}" -ne 0 ]]
  [[ "${output}" == *"KeyError: 'SMS_JID'"* ]]
}

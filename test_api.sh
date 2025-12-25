#!/bin/bash

API_URL="${API_URL:-http://localhost:8001}"
TEST_USER_ID="test_user_$(date +%s)_$$"
TEST_UID="123456789"
TEST_CHANNEL="test_channel_$(date +%s)_$$"
TEST_ROOM_NAME="Test Room $(date '+%Y-%m-%d %H:%M:%S')"

RED='\033[0;31m' GREEN='\033[0;32m' YELLOW='\033[1;33m' 
BLUE='\033[0;34m' PURPLE='\033[0;35m' CYAN='\033[0;36m' NC='\033[0m'

log_success() { echo -e "${GREEN}OK$NC"; }
log_error() { echo -e "${RED}FAILED$NC"; }
log_info() { echo -e "${CYAN}$1$NC"; }

echo "Agora Token Service - Test"
echo "$TEST_USER_ID | $API_URL"
echo "=============================================="

PASSED=0 FAILED=0

log_info "1. Health Check:"
curl -s "$API_URL/health" | head -3
curl -s -w "Code: %{http_code}\n" "$API_URL/health" | tail -1 | grep "200" && { log_success "Health OK"; PASSED=$((PASSED+1)); } || { log_error "Health FAILED"; FAILED=$((FAILED+1)); }
echo

log_info "2. Swagger Docs:"
curl -s -I "$API_URL/docs" | head -1
curl -s -w "Code: %{http_code}\n" "$API_URL/docs" | tail -1 | grep "200" && { log_success "Docs OK"; PASSED=$((PASSED+1)); } || { log_error "Docs FAILED"; FAILED=$((FAILED+1)); }
echo

log_info "3. Simple Auth:"
result=$(curl -s -w "Code: %{http_code}\n" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" \
  -X POST -d '{}' \
  "$API_URL/api/auth")
echo "$result" | head -1
echo "$result" | tail -1 | grep "200" && { log_success "Auth OK"; PASSED=$((PASSED+1)); } || { log_error "Auth FAILED"; FAILED=$((FAILED+1)); }
echo

log_info "4. Create Room:"
room_body="{\"name\": \"$TEST_ROOM_NAME\", \"is_private\": false, \"max_participants\": 10}"
result=$(curl -s -w "Code: %{http_code}\n" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" \
  -X POST -d "$room_body" \
  "$API_URL/api/rooms/")
echo "$result" | head -1
room_code=$(echo "$result" | tail -1)
if [[ "$room_code" == *"200"* ]]; then
    log_success "Room OK"
    TEST_CHANNEL=$(echo "$result" | grep -o '"channel_name":"[^"]*' | cut -d'"' -f4 | head -1 || echo "test_channel")
    log_info "Channel: $TEST_CHANNEL"
    PASSED=$((PASSED+1))
else
    log_error "Room FAILED ($room_code)"
    TEST_CHANNEL="test_channel"
    FAILED=$((FAILED+1))
fi
echo

log_info "5. RTC Token:"
rtc_body="{\"channel\": \"$TEST_CHANNEL\", \"uid\": \"$TEST_UID\", \"role\": \"host\"}"
result=$(curl -s -w "Code: %{http_code}\n" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" \
  -X POST -d "$rtc_body" \
  "$API_URL/api/tokens/rtc")
echo "$result" | head -1
echo "$result" | tail -1 | grep "200" && { log_success "RTC OK"; PASSED=$((PASSED+1)); } || { log_error "RTC FAILED"; FAILED=$((FAILED+1)); }
echo

log_info "6. RTM Token:"
rtm_body="{\"uid\": \"$TEST_UID\"}"
result=$(curl -s -w "Code: %{http_code}\n" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" \
  -X POST -d "$rtm_body" \
  "$API_URL/api/tokens/rtm")
echo "$result" | head -1
echo "$result" | tail -1 | grep "200" && { log_success "RTM OK"; PASSED=$((PASSED+1)); } || { log_error "RTM FAILED"; FAILED=$((FAILED+1)); }
echo

log_info "7. Dual Tokens:"
dual_body="{\"channel\": \"$TEST_CHANNEL\", \"uid\": \"$TEST_UID\", \"role\": \"host\"}"
result=$(curl -s -w "Code: %{http_code}\n" \
  -H "X-User-Id: $TEST_USER_ID" \
  -H "Content-Type: application/json" \
  -X POST -d "$dual_body" \
  "$API_URL/api/tokens/dual")
echo "$result" | head -1
echo "$result" | tail -1 | grep "200" && { log_success "Dual OK"; PASSED=$((PASSED+1)); } || { log_error "Dual FAILED"; FAILED=$((FAILED+1)); }
echo

echo "=============================================="
echo "Result: $PASSED/$FAILED of 7"
echo "User ID: $TEST_USER_ID"
echo "Channel: $TEST_CHANNEL"
echo "Docs: $API_URL/docs"
echo

[[ $FAILED -eq 0 ]] && log_success "ALL TESTS PASSED" || log_info "$FAILED tests failed"
log_info "docker compose logs api"

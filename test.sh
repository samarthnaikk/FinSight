#!/usr/bin/env bash
# FinSight Backend – FULL test suite (fresh DB, continue-on-failure)

API_URL="http://127.0.0.1:8000"
FAIL_COUNT=0
PASS_COUNT=0

# Test user credentials
USER1_NAME="John Doe"
USER1_USERNAME="johndoe"
USER1_EMAIL="john@example.com"
USER1_PASSWORD="Test1234"

USER2_NAME="Jane Smith"
USER2_USERNAME="janesmith"
USER2_EMAIL="jane@example.com"
USER2_PASSWORD="Test5678"

# ----------------- colors -----------------
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
BLUE="\033[0;34m"
CYAN="\033[0;36m"
RESET="\033[0m"
BOLD="\033[1m"

# ----------------- helpers -----------------
log() { echo -e "${CYAN}[$(date '+%F %T')]${RESET} $1" >&2; }
pass() { log "${GREEN}PASS${RESET}: $1"; PASS_COUNT=$((PASS_COUNT+1)); }
fail() { log "${RED}FAIL${RESET}: $1"; FAIL_COUNT=$((FAIL_COUNT+1)); }
section() { echo -e "\n${BOLD}${BLUE}========== $1 ==========${RESET}\n"; }
# Extract JSON field without jq (works in Git Bash on Windows)
extract() { 
  local json="$1"
  local field="$2"
  # Remove the leading dot from field name (e.g., ".access" -> "access")
  field="${field#.}"
  echo "$json" | grep -o "\"$field\":\"[^\"]*\"" | sed "s/\"$field\":\"//" | sed 's/"$//'
}

# =========================================================
# DATABASE INITIALIZATION
# =========================================================
section "Database Initialization"

cd backend || { echo "backend/ folder not found"; exit 1; }

log "Removing old database..."
rm -f db.sqlite3
[[ ! -f db.sqlite3 ]] && pass "Old database removed" || fail "Failed to remove database"

log "Running migrations..."
python manage.py migrate --noinput > /dev/null 2>&1
[[ $? -eq 0 ]] && pass "Migrations completed" || fail "Migrations failed"

cd ..

# =========================================================
# SERVER HEALTH CHECK
# =========================================================
section "Server Health Check"

# Check if server is running
curl -s "$API_URL/" > /dev/null 2>&1
if [[ $? -eq 0 ]]; then
  pass "Server is running on port 8000"
else
  fail "Server is not running on port 8000 - Please start with: python manage.py runserver"
  echo -e "\n${YELLOW}${BOLD}Please run 'python manage.py runserver' in a separate terminal${RESET}\n"
  exit 1
fi

# =========================================================
# USER REGISTRATION
# =========================================================
section "User Registration"

log "Registering User 1..."
res=$(curl -s -X POST "$API_URL/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$USER1_NAME\",\"username\":\"$USER1_USERNAME\",\"email\":\"$USER1_EMAIL\",\"password\":\"$USER1_PASSWORD\"}")
echo "$res" | grep -q '"success"' \
  && pass "User 1 registration successful" || fail "User 1 registration failed: $res"

log "Registering User 2..."
res=$(curl -s -X POST "$API_URL/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"$USER2_NAME\",\"username\":\"$USER2_USERNAME\",\"email\":\"$USER2_EMAIL\",\"password\":\"$USER2_PASSWORD\"}")
echo "$res" | grep -q '"success"' \
  && pass "User 2 registration successful" || fail "User 2 registration failed: $res"

log "Testing duplicate username validation..."
res=$(curl -s -X POST "$API_URL/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test User\",\"username\":\"$USER1_USERNAME\",\"email\":\"test@example.com\",\"password\":\"Test9999\"}")
echo "$res" | grep -qi "username" \
  && pass "Duplicate username validation works" || fail "Duplicate username validation failed"

log "Testing missing field validation..."
res=$(curl -s -X POST "$API_URL/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"testuser\",\"email\":\"test@example.com\"}")
echo "$res" | grep -qi "password\|required" \
  && pass "Missing field validation works" || fail "Missing field validation failed"

# =========================================================
# USER LOGIN
# =========================================================
section "User Login"

log "Login with username..."
res=$(curl -s -X POST "$API_URL/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{\"identifier\":\"$USER1_USERNAME\",\"password\":\"$USER1_PASSWORD\"}")
USER1_ACCESS_TOKEN=$(extract "$res" '.access')
USER1_REFRESH_TOKEN=$(extract "$res" '.refresh')
[[ -n "$USER1_ACCESS_TOKEN" && "$USER1_ACCESS_TOKEN" != "null" ]] \
  && pass "Login with username successful (token: ${USER1_ACCESS_TOKEN:0:20}...)" || fail "Login with username failed: $res"

log "Login with email..."
res=$(curl -s -X POST "$API_URL/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{\"identifier\":\"$USER2_EMAIL\",\"password\":\"$USER2_PASSWORD\"}")
USER2_ACCESS_TOKEN=$(extract "$res" '.access')
USER2_REFRESH_TOKEN=$(extract "$res" '.refresh')
[[ -n "$USER2_ACCESS_TOKEN" && "$USER2_ACCESS_TOKEN" != "null" ]] \
  && pass "Login with email successful (token: ${USER2_ACCESS_TOKEN:0:20}...)" || fail "Login with email failed: $res"

log "Testing invalid credentials..."
res=$(curl -s -X POST "$API_URL/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{\"identifier\":\"$USER1_USERNAME\",\"password\":\"WrongPassword\"}")
echo "$res" | grep -qi "invalid\|error" \
  && pass "Invalid credentials rejected" || fail "Invalid credentials check failed"

log "Testing missing identifier..."
res=$(curl -s -X POST "$API_URL/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d "{\"password\":\"$USER1_PASSWORD\"}")
echo "$res" | grep -qi "error\|required" \
  && pass "Missing identifier validation works" || fail "Missing identifier validation failed"

# =========================================================
# AUTHENTICATED ENDPOINTS
# =========================================================
section "Authenticated Endpoints"

log "Fetching User 1 profile..."
res=$(curl -s -X GET "$API_URL/api/auth/me/" \
  -H "Authorization: Bearer $USER1_ACCESS_TOKEN")
echo "$res" | grep -q "$USER1_USERNAME" \
  && pass "User 1 profile retrieved successfully" || fail "User 1 profile retrieval failed: $res"

log "Verifying User 1 details..."
echo "$res" | grep -q "$USER1_EMAIL" \
  && pass "User 1 email correct" || fail "User 1 email mismatch"
echo "$res" | grep -q "$USER1_NAME" \
  && pass "User 1 name correct" || fail "User 1 name mismatch"

log "Fetching User 2 profile..."
res=$(curl -s -X GET "$API_URL/api/auth/me/" \
  -H "Authorization: Bearer $USER2_ACCESS_TOKEN")
echo "$res" | grep -q "$USER2_USERNAME" \
  && pass "User 2 profile retrieved successfully" || fail "User 2 profile retrieval failed: $res"

log "Testing unauthorized access..."
res=$(curl -s -X GET "$API_URL/api/auth/me/")
echo "$res" | grep -qi "credentials\|authentication\|unauthorized" \
  && pass "Unauthorized access blocked" || fail "Unauthorized access not blocked: $res"

log "Testing invalid token..."
res=$(curl -s -X GET "$API_URL/api/auth/me/" \
  -H "Authorization: Bearer invalid_token_12345")
echo "$res" | grep -qi "invalid\|unauthorized\|credentials" \
  && pass "Invalid token rejected" || fail "Invalid token check failed"

# =========================================================
# TOKEN VERIFICATION
# =========================================================
section "Token Verification"

log "Verifying access token structure..."
DOT_COUNT=$(echo "$USER1_ACCESS_TOKEN" | grep -o '\.' | wc -l | tr -d ' ')
[[ "$DOT_COUNT" -eq 2 ]] \
  && pass "Access token has valid JWT structure (3 parts)" || fail "Access token structure invalid (expected 2 dots, got $DOT_COUNT)"

log "Verifying refresh token structure..."
DOT_COUNT=$(echo "$USER1_REFRESH_TOKEN" | grep -o '\.' | wc -l | tr -d ' ')
[[ "$DOT_COUNT" -eq 2 ]] \
  && pass "Refresh token has valid JWT structure (3 parts)" || fail "Refresh token structure invalid (expected 2 dots, got $DOT_COUNT)"

# =========================================================
# SUMMARY
# =========================================================
section "Summary"
echo -e "${BOLD}Passed:${RESET} ${GREEN}$PASS_COUNT${RESET}"
echo -e "${BOLD}Failed:${RESET} ${RED}$FAIL_COUNT${RESET}"
echo -e "${BOLD}Total:${RESET}  $((PASS_COUNT + FAIL_COUNT))"

if [ "$FAIL_COUNT" -eq 0 ]; then
  echo -e "\n${GREEN}${BOLD}ALL TESTS PASSED ✔${RESET}\n"
  exit 0
else
  echo -e "\n${YELLOW}${BOLD}TESTS COMPLETED WITH $FAIL_COUNT FAILURE(S) ⚠${RESET}\n"
  exit 1
fi

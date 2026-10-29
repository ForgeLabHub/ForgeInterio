#!/usr/bin/env bash
# Проверка живого инстанса Interio.
set -uo pipefail
base="${1:-http://localhost:8000}"
failures=0
ok()  { printf '  \033[32mok\033[0m    %s\n' "$1"; }
bad() { printf '  \033[31mfail\033[0m  %s\n' "$1"; failures=$((failures+1)); }
code() { curl -s -o /dev/null -w '%{http_code}' -m 10 "$@"; }

printf '\nSmoke test: %s\n' "$base"
c="$(code "$base/")";       [ "$c" = "200" ] && ok "GET / -> 200" || bad "GET / -> $c"
c="$(code "$base/quiz")";   [ "$c" = "200" ] && ok "GET /quiz -> 200" || bad "GET /quiz -> $c"
c="$(code "$base/admin")";  [ "$c" = "200" ] && ok "GET /admin -> 200" || bad "GET /admin -> $c"
c="$(code "$base/api/auth/current-user")"
case "$c" in 200) ok "GET /api/auth/current-user -> 200 (без сессии: success=false)";; *) bad "GET /api/auth/current-user -> $c";; esac
c="$(code "$base/api/admin/submissions")"
case "$c" in 401|403) ok "GET /api/admin/submissions -> $c (доступ закрыт)";; *) bad "GET /api/admin/submissions -> $c — админ-данные доступны без прав";; esac

printf '\n'
[ "$failures" -gt 0 ] && { printf '\033[31mпровалено: %d\033[0m\n' "$failures"; exit 1; }
printf '\033[32mSmoke test пройден\033[0m\n'

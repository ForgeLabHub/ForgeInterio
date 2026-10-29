#!/usr/bin/env bash
# Проверка окружения. Ничего не устанавливает и не меняет.
set -uo pipefail
PORT="${PORT:-8000}"
failures=0; warnings=0
ok()   { printf '  \033[32mok\033[0m    %s\n' "$1"; }
bad()  { printf '  \033[31mfail\033[0m  %s\n' "$1"; failures=$((failures+1)); }
warn() { printf '  \033[33mwarn\033[0m  %s\n' "$1"; warnings=$((warnings+1)); }

printf '\nИнструменты\n'
command -v python3 >/dev/null 2>&1 && ok "python $(python3 -V 2>&1 | awk '{print $2}')" || bad "python3 не найден"
command -v git >/dev/null 2>&1 && ok "git" || bad "git не найден"

printf '\nЗависимости\n'
python3 - <<'PY' 2>/dev/null || warn "зависимости не установлены: make install"
import importlib.util
missing = [m for m in ("fastapi", "uvicorn", "pydantic", "requests") if not importlib.util.find_spec(m)]
if missing:
    raise SystemExit(1)
print("  \033[32mok\033[0m    fastapi, uvicorn, pydantic, requests установлены")
PY

printf '\nКонфигурация и секреты\n'
if [ -f .env ]; then ok ".env присутствует"; else warn ".env отсутствует: cp .env.example .env"; fi
if grep -q '^ADMIN_CODE=.\+' .env 2>/dev/null; then
  ok "ADMIN_CODE задан"
  grep -q '^ADMIN_CODE=change-me' .env && bad "ADMIN_CODE оставлен как в примере"
else
  warn "ADMIN_CODE не задан — админ-вход вернёт 503 (это fail closed, а не ошибка)"
fi
if grep -q 'xtsdtjlhsantqhqi' server.py 2>/dev/null; then
  bad "в server.py найден пароль приложения Gmail — удалите и перевыпустите"
else
  ok "секретов в коде нет"
fi
if git ls-files --error-unmatch .env >/dev/null 2>&1; then bad ".env под контролем версий"; else ok ".env не отслеживается git"; fi

printf '\nПорт\n'
if command -v ss >/dev/null 2>&1 && ss -ltn 2>/dev/null | grep -q ":$PORT "; then warn "порт $PORT занят"; else ok "порт $PORT свободен"; fi

printf '\n'
if [ "$failures" -gt 0 ]; then printf '\033[31m%d проверок провалено\033[0m, предупреждений: %d\n' "$failures" "$warnings"; exit 1; fi
printf '\033[32mГотово к работе\033[0m, предупреждений: %d\n' "$warnings"

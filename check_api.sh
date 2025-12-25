#!/bin/bash

API_URL="http://localhost:8001"

echo " Проверка API Agora Token Service"
echo "===================================="

echo "1. Health check (проверка доступности):"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" "$API_URL/health"
echo "Response body:"
curl -s "$API_URL/health"

echo -e "\n2. Документация:"
curl -s -o /dev/null -w "HTTP Status: %{http_code}" "$API_URL/docs"
echo " (200 = доступна)"

echo -e "\n3. Проверка простого маршрута:"
curl -s -X GET "$API_URL/api/auth" \
  -H "X-User-Id: test_user_$(date +%s)" \
  -H "Content-Type: application/json"

echo -e "\n Проверка завершена"

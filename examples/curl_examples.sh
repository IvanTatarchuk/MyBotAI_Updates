#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

echo "Health check" && curl -s "$BASE_URL/health" | jq .

echo "\nCreate idea" && curl -s -X POST "$BASE_URL/api/v1/ideas" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Compliance Copilot",
    "description": "Automate GDPR gap analysis and evidence collection for audits.",
    "target_customer": "B2B SaaS companies"
  }' | jq .

echo "\nList ideas" && curl -s "$BASE_URL/api/v1/ideas" | jq .

echo "\nAssess idea" && curl -s -X POST "$BASE_URL/api/v1/assess" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "AI Compliance Copilot",
    "description": "Automate GDPR gap analysis and evidence collection for audits.",
    "market_size_estimate": 2000000000
  }' | jq .


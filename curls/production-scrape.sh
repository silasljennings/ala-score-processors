#!/bin/bash

# Production scrape request (replace with your Cloud Run URL)
CLOUD_RUN_URL="https://ala-score-processors-YOUR_PROJECT_ID.a.run.app"

curl -X POST ${CLOUD_RUN_URL}/scrape \
  -H "Content-Type: application/json" \
  -H "X_ALA_KEY: ${ALA_SCORE_PROCESSOR_SECRET}" \
  -d '{
    "states": ["al"],
    "sport": "football",
    "force": true
  }'
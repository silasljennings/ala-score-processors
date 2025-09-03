#!/bin/bash

# Production finalize request (replace with your Cloud Run URL)
CLOUD_RUN_URL="https://ala-score-processors-1067313274433.us-central1.run.app"

curl -X POST ${CLOUD_RUN_URL}/finalize \
  -H "Content-Type: application/json" \
  -H "X_ALA_KEY: ade2d396-26b8-49b3-b1a1-b788ead6f5ea" \
  -d '{
    "states": ["al"],
    "sport": "football"
  }'

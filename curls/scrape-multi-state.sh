#!/bin/bash

# Scrape multiple states for volleyball
curl -X POST http://localhost:8080/scrape \
  -H "Content-Type: application/json" \
  -H "X_ALA_KEY: ${ALA_SCORE_PROCESSOR_SECRET}" \
  -d '{
    "states": ["al", "ga", "fl", "tn"],
    "sport": "volleyball",
    "force": true
  }'
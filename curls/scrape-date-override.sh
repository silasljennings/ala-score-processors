#!/bin/bash

# Scrape with specific date override
curl -X POST http://localhost:8080/scrape \
  -H "Content-Type: application/json" \
  -H "X_ALA_KEY: ${ALA_SCORE_PROCESSOR_SECRET}" \
  -d '{
    "states": ["al"],
    "sport": "football",
    "date": "2024-11-15",
    "force": true
  }'
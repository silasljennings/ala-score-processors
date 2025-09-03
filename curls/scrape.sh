#!/bin/bash

# Basic scrape request for Alabama football
curl -X POST http://localhost:8080/scrape \
  -H "Content-Type: application/json" \
  -H "X_ALA_KEY: ${ALA_SCORE_PROCESSOR_SECRET}" \
  -d '{
    "states": ["al"],
    "sport": "football",
    "force": true
  }'
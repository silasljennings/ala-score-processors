#!/bin/bash

# Basic finalize request for Alabama football
curl -X POST http://localhost:8080/finalize \
  -H "Content-Type: application/json" \
  -H "X_ALA_KEY: ${ALA_SCORE_PROCESSOR_SECRET}" \
  -d '{
    "states": ["al"],
    "sport": "football"
  }'
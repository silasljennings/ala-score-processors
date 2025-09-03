#!/bin/bash
set -euo pipefail

FILE=$1

echo "Parsing $FILE ..."

SCHEDULE=$(yq -r '.schedule' "$FILE")
TIMEZONE=$(yq -r '.timeZone' "$FILE")
URI=$(yq -r '.httpTarget.uri' "$FILE")
METHOD=$(yq -r '.httpTarget.httpMethod' "$FILE")
SERVICE_ACCOUNT=$(yq -r '.httpTarget.oidcToken.serviceAccountEmail' "$FILE")
HEADERS=$(yq -r '.httpTarget.headers | to_entries | map(.key + "=" + .value) | join(",")' "$FILE")
BODY=$(yq -r '.httpTarget.body' "$FILE")

echo "SCHEDULE: $SCHEDULE"
echo "TIMEZONE: $TIMEZONE"
echo "URI: $URI"
echo "METHOD: $METHOD"
echo "SERVICE_ACCOUNT: $SERVICE_ACCOUNT"
echo "HEADERS: $HEADERS"
echo "BODY: $BODY"

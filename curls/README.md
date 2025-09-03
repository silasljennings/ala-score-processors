# cURL Examples

This directory contains ready-to-use cURL commands for testing the API endpoints.

## Prerequisites

Set your authentication secret as an environment variable:
```bash
export ALA_SCORE_PROCESSOR_SECRET="your-secret-key"
```

## Local Development (localhost:8080)

### Basic Operations
- **`health.sh`** - Check service health and scheduler status
- **`season.sh`** - Get current season information
- **`scrape.sh`** - Basic scrape for Alabama football
- **`finalize.sh`** - Basic finalize for Alabama football

### Advanced Operations
- **`scrape-multi-state.sh`** - Scrape multiple states for volleyball
- **`scrape-date-override.sh`** - Scrape with specific date override
- **`finalize-multi-state.sh`** - Finalize multiple states for volleyball

## Production (Cloud Run)

- **`production-scrape.sh`** - Production scrape (update CLOUD_RUN_URL)
- **`production-finalize.sh`** - Production finalize (update CLOUD_RUN_URL)

## Usage

Make scripts executable and run:
```bash
chmod +x curls/*.sh
./curls/health.sh
./curls/scrape.sh
```

## Authentication

All `/scrape` and `/finalize` endpoints require the `X_ALA_KEY` header. The scripts automatically use the `ALA_SCORE_PROCESSOR_SECRET` environment variable.

## Force Parameter

All scrape scripts use `"force": true` to bypass time window restrictions, allowing manual execution at any time. This is ideal for:
- Testing and debugging
- Manual data collection
- Emergency updates outside scheduled hours

## Response Examples

### Successful Scrape
```json
{
  "ok": true,
  "sport": "football",
  "date": "11/15/2024",
  "inserted": 45,
  "skipped": 2,
  "meta": [
    {"state_code": "al", "count": 47}
  ]
}
```

### Authentication Error
```json
{
  "detail": "X_ALA_KEY header required"
}
```
# MaxPreps Score Scraper - Deployment Guide

This application supports multiple execution modes to replace your Edge Function with a more robust Cloud Run service.

## Execution Modes

### 1. API Server Mode (Default)
Runs as a FastAPI web server with HTTP endpoints.

**Environment Variables:**
- `ENABLE_SCHEDULER=false` (default)

**Endpoints:**
- `POST /scrape` - Manual scraping (your original endpoint)
- `POST /finalize` - Manual score finalization (your new endpoint)
- `POST /trigger/default_scrape` - Trigger default scheduled scrape task
- `POST /trigger/football_scrape` - Trigger football scheduled scrape task
- `POST /trigger/default_finalize` - Trigger default scheduled finalize task
- `POST /trigger/football_finalize` - Trigger football scheduled finalize task
- `GET /health` - Health check

**Usage:**
```bash
# Local
uvicorn main:app --host 0.0.0.0 --port 8080

# Docker
docker run -p 8080:8080 <image>

# Cloud Run (your existing setup)
```

### 2. Scheduler Mode (Cron Replacement)
Runs internal cron-like scheduler with your web server.

**Environment Variables:**
- `ENABLE_SCHEDULER=true`
- `USE_TIMEZONE_SCHEDULES=true`
- `SPORT_SCHEDULES=seasonal` (Options: "seasonal", "fall", "late_fall", "winter", "late_winter", "spring", "football", "volleyball", "all")
- `SCRAPE_SCHEDULE=0 20 * * 3,4,5` (8PM Thu,Fri,Sat - only for simple mode)
- `FOOTBALL_SCHEDULE=0 21 * * 4` (9PM Friday - only for simple mode)
- `FINALIZE_SCHEDULE=0 22 * * 3,4,5` (10PM Thu,Fri,Sat - only for simple mode)
- `FOOTBALL_FINALIZE_SCHEDULE=0 8 * * 5` (8AM Saturday - only for simple mode)

**Cron Format:** `minute hour day month dow`
- `0 20 * * 3,4,5` = 8:00 PM on Thu,Fri,Sat
- `0 21 * * 4` = 9:00 PM on Friday
- `*/15 * * * *` = Every 15 minutes
- `0 */2 * * *` = Every 2 hours

**Usage:**
```bash
# Docker with scheduler
docker run -e ENABLE_SCHEDULER=true <image>

# Docker Compose
docker-compose up scheduler
```

### 3. CLI Mode (One-time Execution)
Execute tasks directly from command line.

**Commands:**
```bash
# Custom scrape
python cli.py scrape --states al,ga,fl --sport football --force

# Custom finalize
python cli.py finalize --states al,ga,fl --sport football

# Default scheduled tasks
python cli.py default           # Default scrape
python cli.py default-finalize  # Default finalize

# Football scheduled tasks  
python cli.py football          # Football scrape
python cli.py football-finalize # Football finalize

# Docker CLI examples
docker run --rm <image> python cli.py scrape --states al --force
docker run --rm <image> python cli.py finalize --states al --sport football
```

## Cloud Run Deployment Options

### Option A: Scheduled Cloud Run Job
Replace your cron trigger with Cloud Run Jobs:

```yaml
# cloudbuild.yaml update
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/scraper', '.']
  - name: 'gcr.io/cloud-builders/docker'  
    args: ['push', 'gcr.io/$PROJECT_ID/scraper']
  
  # Deploy as Job for scheduled execution
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'jobs'
      - 'replace'
      - 'job.yaml'
```

Create `job.yaml`:
```yaml
apiVersion: run.googleapis.com/v1
kind: Job
metadata:
  name: score-scraper-job
spec:
  spec:
    template:
      spec:
        template:
          spec:
            containers:
            - image: gcr.io/PROJECT_ID/scraper
              command: ["python"]
              args: ["cli.py", "default"]
              env:
              - name: SUPABASE_URL
                value: "your-url"
              - name: SUPABASE_SERVICE_ROLE_KEY
                value: "your-key"
```

### Option B: Scheduler-Enabled Service
Single service that handles both API and scheduling:

```bash
gcloud run deploy scraper \
  --image gcr.io/$PROJECT_ID/scraper \
  --set-env-vars ENABLE_SCHEDULER=true \
  --set-env-vars USE_TIMEZONE_SCHEDULES=true \
  --set-env-vars SPORT_SCHEDULES=seasonal \
  --cpu-always-allocated \
  --min-instances 1
```

### Option C: Hybrid (Recommended)
- Keep existing Cloud Run service for API calls
- Add scheduled Cloud Run Jobs for automation

## Environment Variables

```bash
# Database
SUPABASE_URL=your-supabase-url
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# Scraping Config  
STATES=al,ga,fl              # Comma-separated states
SPORT=football               # Default sport
SCRAPE_CONCURRENCY=2         # Concurrent requests
SCRAPE_BATCH_PAUSE_MS=150    # Pause between batches
SCRAPE_RETRIES=2             # Retry failed requests

# Scheduler Config
ENABLE_SCHEDULER=true                    # Enable internal scheduler
USE_TIMEZONE_SCHEDULES=true              # Use timezone-aware schedules (recommended)
SPORT_SCHEDULES=seasonal                 # Seasonal auto-selection (recommended)

# Alternative SPORT_SCHEDULES options:
# SPORT_SCHEDULES=fall                   # Fall season (football + volleyball)
# SPORT_SCHEDULES=late_fall              # Late fall (football + volleyball + basketball)
# SPORT_SCHEDULES=winter                 # Winter (basketball only)
# SPORT_SCHEDULES=late_winter            # Late winter (basketball + baseball + soccer + softball)
# SPORT_SCHEDULES=spring                 # Spring (baseball + softball + soccer)
# SPORT_SCHEDULES=football               # Football only
# SPORT_SCHEDULES=volleyball             # Volleyball only  
# SPORT_SCHEDULES=all                    # All implemented sports

# Simple mode schedules (only used if USE_TIMEZONE_SCHEDULES=false)
SCRAPE_SCHEDULE="0 20 * * 3,4,5"         # Default scrape schedule  
FOOTBALL_SCHEDULE="0 21 * * 4"           # Football scrape schedule
FINALIZE_SCHEDULE="0 22 * * 3,4,5"       # Default finalize schedule
FOOTBALL_FINALIZE_SCHEDULE="0 8 * * 5"   # Football finalize schedule
```

## Migration from Edge Function

Your existing cron setup can be replaced with:

1. **Immediate**: Change cron target to `POST /trigger/default_scrape`
2. **Better**: Deploy with `SPORT_SCHEDULES=seasonal` for automatic season detection
3. **Best**: Use seasonal scheduling for self-contained, intelligent execution

## Seasonal Scheduling (Recommended)

The system automatically detects the current season and enables appropriate sports:

### Current Season Schedule
Check what's active: `GET /season`

### Seasonal Breakdown
- **Fall** (Aug-Nov): Football + Volleyball
- **Late Fall** (Nov-Dec): Football + Volleyball + Basketball*
- **Winter** (Dec-Feb): Basketball*
- **Late Winter** (Feb-Mar): Basketball* + Baseball* + Soccer* + Softball*
- **Spring** (Mar-Jun): Baseball* + Soccer* + Softball*

*Sports marked with * don't have schedules implemented yet (only football and volleyball currently)

### Deployment Examples

```bash
# Seasonal (recommended) - auto-detects current season
SPORT_SCHEDULES=seasonal

# Specific season override
SPORT_SCHEDULES=fall        # Force fall sports regardless of date

# Individual sports
SPORT_SCHEDULES=football    # Football only
SPORT_SCHEDULES=volleyball  # Volleyball only

# All implemented sports
SPORT_SCHEDULES=all         # Both football and volleyball
```

The application maintains 100% backward compatibility with your existing `/scrape` endpoint.
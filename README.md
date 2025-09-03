# MaxPreps Score Processor

A comprehensive FastAPI application for scraping high school sports scores from MaxPreps and storing them in Supabase. Features intelligent seasonal scheduling, timezone-aware cron jobs, and modular architecture.

## 🏈 Overview

This application replaces Supabase Edge Functions with a more robust Cloud Run service that provides:

- **Automated Score Scraping**: Fetches scores from MaxPreps across all US states and timezones
- **Score Finalization**: Updates game states based on score availability
- **Seasonal Intelligence**: Automatically adjusts sports schedules based on current season
- **Timezone Awareness**: Handles all 6 US timezones with proper local time scheduling
- **Modular Architecture**: Clean, maintainable codebase with proper separation of concerns

## 🚀 Quick Start

### Option 1: Seasonal Scheduling (Recommended)
```bash
docker run \
  -e ENABLE_SCHEDULER=true \
  -e USE_TIMEZONE_SCHEDULES=true \
  -e SPORT_SCHEDULES=seasonal \
  -e SUPABASE_URL=your-supabase-url \
  -e SUPABASE_SERVICE_ROLE_KEY=your-service-key \
  -p 8080:8080 \
  your-image
```

### Option 2: Docker Compose
```bash
# Set environment variables
export SUPABASE_URL=your-url
export SUPABASE_SERVICE_ROLE_KEY=your-key

# Run with seasonal scheduling
docker-compose up scheduler
```

### Option 3: Cloud Run (Production)
```bash
gcloud run deploy ala-score-processors \
  --image gcr.io/$PROJECT_ID/ala-score-processors \
  --set-env-vars ENABLE_SCHEDULER=true \
  --set-env-vars USE_TIMEZONE_SCHEDULES=true \
  --set-env-vars SPORT_SCHEDULES=seasonal \
  --cpu-always-allocated \
  --min-instances 1
```

## 📅 Seasonal Scheduling

The system automatically detects the current season and enables appropriate sports:

| Season | Months | Sports | Status |
|--------|---------|---------|--------|
| **Fall** | Aug-Nov | Football + Volleyball | ✅ Implemented |
| **Late Fall** | Nov-Dec | Football + Volleyball + Basketball | 🔄 Partial |
| **Winter** | Dec-Feb | Basketball | 🚧 Future |
| **Late Winter** | Feb-Mar | Basketball + Baseball + Soccer + Softball | 🚧 Future |
| **Spring** | Mar-Jun | Baseball + Softball + Soccer | 🚧 Future |

### Current Implementation
- **Football**: Every 3 minutes during 5PM-11:30PM (Thu-Sat)
- **Volleyball**: Every 15 minutes during 3PM-11PM (Daily)
- **Finalization**: Runs after game completion times per sport

## 🌍 Timezone Coverage

Covers all US states across 6 timezones with proper local time handling:

- **Eastern**: CT, DE, DC, FL, GA, ME, MD, MA, NH, NJ, NY, NC, OH, PA, RI, SC, VT, VA, WV
- **Central**: AL, AR, FL, IA, IL, IN, KY, LA, MI, MN, MS, MO, TN, TX, WI  
- **Mountain**: AZ, CO, ID, KS, MT, NE, NM, ND, OK, SD, UT, WY
- **Pacific**: CA, NV, OR, WA
- **Alaska**: AK
- **Hawaii**: HI

## 📁 Architecture

```
/
├── main.py                     # FastAPI app entry point
├── api/
│   └── routes.py              # API endpoint handlers  
├── config/
│   ├── settings.py            # Environment configuration
│   ├── timezone_schedules.py  # Timezone and sports schedules
│   ├── seasonal_schedules.py  # Seasonal logic
│   └── schedules.yml          # Schedule documentation
├── database/
│   └── supabase_client.py     # Database operations
├── utils/
│   ├── time_helpers.py        # Date/time utilities
│   ├── data_helpers.py        # Data processing utilities
│   └── url_helpers.py         # URL building and parsing
├── scraper/
│   ├── web_client.py          # HTTP client with retry logic
│   └── score_scraper.py       # HTML parsing and extraction
├── scheduler/
│   ├── cron_scheduler.py      # Basic cron scheduler
│   ├── advanced_scheduler.py  # Timezone-aware scheduler
│   ├── timezone_tasks.py      # Timezone-specific tasks
│   └── tasks.py               # Scheduled task definitions
├── finalize/
│   └── score_finalizer.py     # Score finalization logic
├── cli.py                     # Command line interface
├── docker-compose.yml         # Multi-service deployment
├── Dockerfile                 # Container definition
└── cloudbuild.yaml           # Google Cloud Build pipeline
```

## 🔧 Configuration

### Environment Variables

#### Required
```bash
SUPABASE_URL=your-supabase-url                    # Database URL
SUPABASE_SERVICE_ROLE_KEY=your-service-key        # Database auth key
ALA_SCORE_PROCESSOR_SECRET=your-secret-key        # API authentication secret
```

#### Scheduling (Optional)
```bash
ENABLE_SCHEDULER=true                             # Enable internal scheduler
USE_TIMEZONE_SCHEDULES=true                       # Use timezone-aware schedules
SPORT_SCHEDULES=seasonal                          # Seasonal auto-selection

# Alternative SPORT_SCHEDULES options:
# SPORT_SCHEDULES=fall                            # Fall season only
# SPORT_SCHEDULES=football                        # Football only
# SPORT_SCHEDULES=volleyball                      # Volleyball only
# SPORT_SCHEDULES=all                             # All implemented sports
```

#### Optional Tuning
```bash
STATES=al,ga,fl                                   # Override default states
SCRAPE_CONCURRENCY=2                              # Concurrent requests
SCRAPE_BATCH_PAUSE_MS=150                         # Pause between batches
SCRAPE_RETRIES=2                                  # Retry failed requests
```

## 📡 API Endpoints

### Core Operations
- `POST /scrape` - Manual score scraping (requires X_ALA_KEY header)
- `POST /finalize` - Manual score finalization (requires X_ALA_KEY header)
- `GET /health` - Health check with scheduler status
- `GET /season` - Current season information

### Scheduled Task Triggers
- `POST /trigger/default_scrape` - Trigger default scraping
- `POST /trigger/default_finalize` - Trigger default finalization
- `POST /trigger/timezone/scrape/{timezone}?sport=football` - Timezone-specific scraping
- `POST /trigger/volleyball/scrape` - All-timezone volleyball scraping

## 💻 Command Line Interface

### Basic Commands
```bash
# Custom scraping
python cli.py scrape --states al,ga --sport football --force

# Scheduled tasks
python cli.py default                             # Default scrape
python cli.py default-finalize                   # Default finalize
python cli.py football                           # Football scrape  
python cli.py football-finalize                  # Football finalize

# Timezone-specific
python cli.py timezone-scrape eastern --sport volleyball
python cli.py timezone-finalize pacific --sport football

# Volleyball across all timezones
python cli.py volleyball-scrape-all
python cli.py volleyball-finalize-all
```

### Docker CLI
```bash
# Run custom scrape
docker run --rm <image> python cli.py scrape --states al --force

# Run timezone-specific volleyball
docker run --rm <image> python cli.py timezone-scrape eastern --sport volleyball
```

## 🏗️ Deployment Options

### 1. Cloud Build (Production)
Uses the included `cloudbuild.yaml` for automated CI/CD:

```bash
# Trigger build and deploy
gcloud builds submit --config cloudbuild.yaml
```

The Cloud Build pipeline:
1. Builds Docker image
2. Pushes to Artifact Registry  
3. Deploys to Cloud Run with scheduling enabled
4. Configures proper resource allocation for continuous operation

### 2. Docker Compose (Development)
```bash
# API server mode
docker-compose up api

# Scheduler mode  
docker-compose up scheduler

# CLI mode
docker-compose run --rm cli scrape --states al --force
```

### 3. Cloud Run Jobs (Alternative)
For scheduled execution without persistent containers:

```bash
gcloud run jobs create score-scraper-job \
  --image gcr.io/$PROJECT_ID/scraper \
  --command python \
  --args cli.py,default \
  --set-env-vars SUPABASE_URL=$SUPABASE_URL
```

## 📊 Monitoring

### Health Check
```bash
curl https://your-service/health
```

Response includes:
- Scheduler status and task count
- Current season information  
- Configuration details
- Service health

### Season Information
```bash
curl https://your-service/season
```

Returns current season, active sports, and schedule details.

### Logs
Monitor Cloud Run logs for:
- Schedule execution confirmations
- Scraping results and statistics
- Error handling and retries
- Season transitions

## 🔄 Migration from Edge Functions

This application replaces Supabase Edge Functions and cron jobs:

### Before (Edge Functions + Cron)
- 33 separate Supabase cron schedules
- External dependency on Supabase cron service
- Manual timezone and season management
- Limited processing time and memory

### After (Cloud Run Service)
- Single self-contained service
- Internal scheduling with 33+ timezone-aware tasks
- Automatic seasonal sports detection
- Up to 60 minutes processing time and 32GB memory
- Cost-effective and maintainable

### Migration Steps
1. Deploy this service with scheduling enabled
2. Verify schedules are running via `/health` endpoint
3. Disable old Supabase cron schedules
4. Monitor for smooth operation

## 🧪 Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
uvicorn main:app --reload --host 0.0.0.0 --port 8080

# Run CLI commands
python cli.py scrape --states al --sport football

# Run with scheduler (development)
ENABLE_SCHEDULER=true USE_TIMEZONE_SCHEDULES=true python -c "import uvicorn; uvicorn.run('main:app', host='0.0.0.0', port=8080)"
```

### Testing
```bash
# Test syntax
python -c "import ast; [ast.parse(open(f).read()) for f in ['main.py', 'cli.py']]"

# Test imports
python -c "from main import app; print('✓ Main app import successful')"

# Manual test endpoints
curl -X POST http://localhost:8080/scrape \
  -H "Content-Type: application/json" \
  -H "X_ALA_KEY: your-secret-key" \
  -d '{"states":"al","sport":"football","force":true}'
```

### Adding New Sports
1. Add sport schedules to `config/timezone_schedules.py`
2. Update `scheduler/advanced_scheduler.py` with setup methods
3. Add to seasonal configuration in `config/seasonal_schedules.py`
4. Update CLI commands in `cli.py`
5. Add API endpoints in `main.py`

## 📚 Dependencies

- **FastAPI**: Web framework and API server
- **httpx**: Async HTTP client for web scraping
- **BeautifulSoup4**: HTML parsing and data extraction
- **Supabase**: Database client and operations
- **pytz**: Timezone handling and calculations
- **uvicorn**: ASGI server for production deployment

## 🔒 Security

- Environment variables for sensitive data (database credentials, API secrets)
- API key authentication via X_ALA_KEY header for all scraping/finalization endpoints
- Service role authentication for Supabase
- Rate limiting and polite scraping practices
- Input validation and error handling
- No hardcoded secrets in codebase

## 📈 Performance

- Configurable concurrency for scraping operations
- Intelligent rate limiting and retry logic
- Batch processing for database operations
- Timezone-optimized scheduling to reduce unnecessary runs
- Efficient HTML parsing with CSS selectors

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the existing modular architecture
4. Test thoroughly with various configurations
5. Submit a pull request with clear description

## 📄 License

This project is proprietary software for high school sports score processing.

---

## 🎯 Current Status

- ✅ **Football Scheduling**: Complete with timezone awareness
- ✅ **Volleyball Scheduling**: Complete with timezone awareness  
- ✅ **Seasonal Detection**: Automatic season-based sport selection
- ✅ **Cloud Run Deployment**: Production-ready with Cloud Build
- ✅ **API Compatibility**: Full backward compatibility maintained
- 🚧 **Basketball Scheduling**: Future implementation planned
- 🚧 **Baseball/Softball Scheduling**: Future implementation planned
- 🚧 **Soccer Scheduling**: Future implementation planned

For questions or support, refer to the deployment documentation in `DEPLOYMENT.md`.
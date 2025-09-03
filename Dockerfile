FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Support multiple run modes: API server, scheduler, or CLI
# Default: API server mode
# Set ENABLE_SCHEDULER=true for scheduled mode
# Use CLI: docker run <image> python cli.py <command>
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]


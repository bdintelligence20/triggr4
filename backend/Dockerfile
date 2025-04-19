FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for document processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils \
    libmagic1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create upload directory
RUN mkdir -p /tmp/uploads

# Set environment variables
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV GUNICORN_TIMEOUT=120
ENV GUNICORN_WORKERS=2

# Add a health check script
RUN echo '#!/bin/bash\ncurl -f http://localhost:$PORT/health || exit 1' > /app/healthcheck.sh \
    && chmod +x /app/healthcheck.sh

# Add a startup script
RUN echo '#!/bin/bash\n\
echo "Starting Knowledge Hub backend on port $PORT"\n\
echo "Workers: $GUNICORN_WORKERS, Timeout: $GUNICORN_TIMEOUT"\n\
exec gunicorn --config gunicorn_config.py app:app\n\
' > /app/start.sh \
    && chmod +x /app/start.sh

# Run the application with the startup script
CMD ["/app/start.sh"]

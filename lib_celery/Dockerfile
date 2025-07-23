FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire project context to access lib_mongodb
COPY . .

# Install healthcare-mongodb first (local dependency)
RUN cd lib_mongodb && pip install -e .

# Install the Celery package using pip
RUN cd lib_celery && pip install -e .

# Add the project root to Python path
ENV PYTHONPATH=/app/lib_celery:/app/lib_mongodb:$PYTHONPATH

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Create directories for Celery
RUN mkdir -p /tmp/celery

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command - run the worker
CMD ["celery", "-A", "healthcare_celery.app", "worker", "--loglevel=info"] 
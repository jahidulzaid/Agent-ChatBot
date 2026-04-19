# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy build context and normalize paths so this Dockerfile works when
# context is either repository root or backend directory.
COPY . /workspace

RUN if [ -f /workspace/requirements.txt ]; then \
            cp /workspace/requirements.txt /app/requirements.txt; \
            cp -r /workspace/. /app/; \
        elif [ -f /workspace/backend/requirements.txt ]; then \
            cp /workspace/backend/requirements.txt /app/requirements.txt; \
            cp -r /workspace/backend/. /app/; \
        else \
            echo "requirements.txt not found in build context"; \
            exit 1; \
        fi && rm -rf /workspace

# Install Python dependencies
RUN pip install --no-cache-dir --extra-index-url https://download.pytorch.org/whl/cpu torch==2.5.1+cpu \
    && pip install --no-cache-dir -r /app/requirements.txt \
    && apt-get purge -y --auto-remove gcc g++ make \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories
RUN mkdir -p data/chromadb data/uploads

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=5)" || exit 1

# Run the application
CMD ["python", "main.py"]

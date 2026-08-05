# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for packet capture
RUN apt-get update && apt-get install -y \
    libpcap-dev \
    tcpdump \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for logs and database
RUN mkdir -p logs

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose Flask dashboard port
EXPOSE 5000

# Run as non-root user for security
RUN useradd -m -u 1000 netsentinel && \
    chown -R netsentinel:netsentinel /app
USER netsentinel

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000', timeout=5)" || exit 1

# Start NetSentinel
CMD ["python", "main.py"]

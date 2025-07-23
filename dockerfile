# Use the official Python image as the base
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Install system dependencies (for psycopg2, etc.)
RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your code
COPY . .

# Expose port
EXPOSE 8000

# Set environment variables (optional, for Python output buffering)
ENV PYTHONUNBUFFERED=1

COPY start.sh /start.sh

RUN chmod +x /start.sh

# Run the FastAPI app with Uvicorn
CMD ["/start.sh"]
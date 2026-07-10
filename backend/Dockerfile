FROM python:3.12-slim

# System deps for psycopg2-binary
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default: run the FastAPI server
# Override in docker-compose for the worker service
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

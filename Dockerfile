# Use a minimal base image
FROM python:3.9-slim as base

# Set environment variables to avoid Python cache and set timezone
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=UTC

# Set work directory
WORKDIR /app

# Install essential system dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies (CPU-only PyTorch via direct link)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html

# Copy the application code
COPY . .

# Remove Python cache
RUN find . -type d -name "__pycache__" -exec rm -rf {} + && \
    rm -rf /root/.cache /tmp/*

# Expose the port for FastAPI
EXPOSE 7860

# Start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

FROM python:3.9-slim-bullseye

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/python \
    TRANSFORMERS_CACHE=/app/models

# Install minimal required system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    binutils \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /root/.cache

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies directly into /app/python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --target=/app/python --find-links https://download.pytorch.org/whl/cpu/torch_stable.html

# Copy application code
COPY . .

# Clean __pycache__ and strip shared libs
RUN find . -type d -name "__pycache__" -exec rm -rf {} + && \
    find /app/python -type d -name "__pycache__" -exec rm -rf {} + && \
    find /app/python -name '*.so' -exec strip --strip-unneeded {} + || true

# Expose FastAPI port
EXPOSE 7860

# Start FastAPI with uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

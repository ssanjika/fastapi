# Use official Python 3.9 slim image
FROM python:3.9-slim

# Set working directory and environment variables
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/app/.cache/huggingface

# Install system dependencies needed for torch and transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for caching
COPY requirements.txt .

# Install Python dependencies using the CPU-only torch wheels from PyTorch official repo
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html

# Copy only your app code now
COPY . .

# Clear caches to reduce image size
RUN rm -rf /root/.cache/pip /root/.cache/huggingface /tmp/*

# Expose port and command to run app
EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

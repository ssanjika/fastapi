FROM python:3.9-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/app/.cache/huggingface

# Install minimal dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for caching
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html

# Copy your application code
COPY . .

# Clean pip cache and temp files after install
RUN rm -rf /root/.cache/pip /root/.cache/huggingface /tmp/*

EXPOSE 7860

# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860", \
     "--timeout-keep-alive", "400", "--workers", "2"]
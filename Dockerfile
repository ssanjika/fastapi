# Stage 1: Builder with build-time dependencies
FROM python:3.9-slim-bullseye as builder

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/app/models

# Install build essentials and clean in same layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt . 
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html

# Download models and clean cache
RUN python -c "from transformers import AutoModel, AutoTokenizer; \
    AutoModel.from_pretrained('ProsusAI/finbert'); \
    AutoTokenizer.from_pretrained('ProsusAI/finbert'); \
    AutoModel.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment'); \
    AutoTokenizer.from_pretrained('nlptown/bert-base-multilingual-uncased-sentiment')" \
    && rm -rf /root/.cache/huggingface

# Stage 2: Runtime image
FROM python:3.9-slim-bullseye

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TRANSFORMERS_CACHE=/app/models \
    PATH="/opt/venv/bin:$PATH"

# Install runtime dependencies and binutils (for strip)
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 binutils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /root/.cache

# Copy virtual environment and models from builder
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/models /app/models
COPY . .

# Clean up __pycache__ and strip shared libs to reduce size
RUN find /opt/venv -type d -name '__pycache__' -exec rm -rf {} + && \
    find . -type d -name '__pycache__' -exec rm -rf {} + && \
    find /opt/venv -name '*.so' -exec strip --strip-unneeded {} +

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

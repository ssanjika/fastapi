# Use official Python slim image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app
# Copy requirements and install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt --find-links https://download.pytorch.org/whl/torch_stable.html

# Copy the entire project into the container
COPY . .

# Cleanup unnecessary files
RUN find . -type d -name "__pycache__" -exec rm -rf {} + && \
    rm -rf /root/.cache /tmp/*
# Expose port 7860 (required by Hugging Face Spaces)
EXPOSE 7860

# Run the FastAPI app with Uvicorn on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]

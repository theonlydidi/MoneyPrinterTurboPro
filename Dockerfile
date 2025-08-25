# Multi-stage Docker build for MoneyPrinterTurboPro
# Stage 1: Base image with system dependencies
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg \
    imagemagick \
    libmagickwand-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && mkdir -p /app /cache /temp /output /storage /logs \
    && chown -R app:app /app /cache /temp /output /storage /logs

# Stage 2: Python dependencies
FROM base as dependencies

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Application build
FROM dependencies as builder

# Copy application code
COPY . .

# Install development dependencies for building
RUN pip install --no-cache-dir -r requirements-dev.txt

# Run any build steps (if needed)
RUN python -m compileall app/ webui/

# Stage 4: Production image
FROM base as production

# Set working directory
WORKDIR /app

# Copy Python dependencies from dependencies stage
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy application code from builder stage
COPY --from=builder /app /app

# Copy system dependencies
COPY --from=base /usr/bin/ffmpeg /usr/bin/ffmpeg
COPY --from=base /usr/bin/convert /usr/bin/convert

# Create necessary directories
RUN mkdir -p /app/cache /app/temp /app/output /app/storage /app/logs /app/models

# Set ownership
RUN chown -R app:app /app

# Switch to non-root user
USER app

# Set environment variables
ENV PYTHONPATH=/app \
    MONEYPRINTER_PRO_ENV=production \
    MONEYPRINTER_PRO_HOST=0.0.0.0 \
    MONEYPRINTER_PRO_API_PORT=8080 \
    MONEYPRINTER_PRO_WEBUI_PORT=8501

# Expose ports
EXPOSE 8080 8501 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["python", "run.py"]

# Stage 5: Development image
FROM dependencies as development

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Install development dependencies
RUN pip install --no-cache-dir -r requirements-dev.txt

# Set environment variables
ENV PYTHONPATH=/app \
    MONEYPRINTER_PRO_ENV=development \
    MONEYPRINTER_PRO_HOST=0.0.0.0 \
    MONEYPRINTER_PRO_API_PORT=8080 \
    MONEYPRINTER_PRO_WEBUI_PORT=8501 \
    MONEYPRINTER_PRO_RELOAD=true \
    MONEYPRINTER_PRO_LOG_LEVEL=DEBUG

# Expose ports
EXPOSE 8080 8501 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command for development
CMD ["python", "run.py", "--dev"]

# Stage 6: GPU-enabled image
FROM base as gpu

# Install CUDA dependencies (if available)
RUN apt-get update && apt-get install -y \
    nvidia-cuda-toolkit \
    nvidia-cuda-runtime \
    && rm -rf /var/lib/apt/lists/*

# Copy from production stage
COPY --from=production /app /app
COPY --from=production /usr/local /usr/local

# Set working directory
WORKDIR /app

# Set environment variables for GPU
ENV CUDA_VISIBLE_DEVICES=0 \
    NVIDIA_VISIBLE_DEVICES=all \
    NVIDIA_DRIVER_CAPABILITIES=compute,utility

# Switch to non-root user
USER app

# Expose ports
EXPOSE 8080 8501 9090

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Default command
CMD ["python", "run.py", "--gpu"]

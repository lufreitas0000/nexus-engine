# Stage 1: Builder
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /build

# Install system build dependencies required for compiling Python packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Compile wheels to avoid transferring compilation toolchains to the final image
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# Stage 2: Production Runtime
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Copy compiled wheels and dependencies from builder
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .

# Install packages from local wheels
RUN pip install --no-cache /wheels/* && \
    rm -rf /wheels

# Copy application source code
COPY . /app/

# Define default execution point (Override in docker-compose.yml for workers/API)
CMD ["python", "-m", "front.app"]

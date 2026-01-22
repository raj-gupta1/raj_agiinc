# AGI Web Agent Docker Image
# Optimized for fast builds

FROM python:3.11-slim AS base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install minimal Playwright dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    fonts-liberation \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd --gid 1000 agent \
    && useradd --uid 1000 --gid agent --shell /bin/bash --create-home agent

WORKDIR /app

# Copy requirements first (better layer caching)
COPY requirements.txt ./
COPY agiwebagent/requirements.txt ./agiwebagent/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir -r agiwebagent/requirements.txt

# Install Playwright browsers (chromium includes headless_shell required by agisdk)
RUN playwright install --with-deps

# Copy application code only (not results, etc.)
COPY --chown=agent:agent agiwebagent/ ./agiwebagent/
COPY --chown=agent:agent agisdk/ ./agisdk/

# Switch to non-root user
USER agent

# Default command
ENTRYPOINT ["python", "agiwebagent/main.py"]
CMD ["--help"]

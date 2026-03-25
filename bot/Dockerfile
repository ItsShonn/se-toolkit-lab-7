# Bot Dockerfile - builds venv inside container with cache
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

# Copy workspace files
COPY pyproject.toml uv.lock ./

# Copy bot source
COPY bot/ ./bot/

# Create venv with cache mount (uses host's uv cache if available)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# Set environment
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "-m", "bot.bot"]

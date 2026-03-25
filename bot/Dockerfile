# Bot Dockerfile - uses uv for dependency management
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

# Set working directory
WORKDIR /app

# Copy bot source code
COPY bot/ ./bot/

# Copy workspace files for dependency resolution
COPY pyproject.toml uv.lock ./

# Install bot dependencies using uv sync from workspace root
RUN uv sync --frozen --no-dev --package bot

# Set environment variables to use the venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "-m", "bot.bot"]

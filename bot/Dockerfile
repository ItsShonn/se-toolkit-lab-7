# Bot Dockerfile - uses uv for dependency management
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

# Set working directory
WORKDIR /app

# Copy workspace files first for dependency resolution
COPY pyproject.toml uv.lock ./

# Copy bot source code
COPY bot/ ./bot/

# Install bot dependencies using uv sync (without --frozen to allow flexibility)
RUN uv sync --no-dev

# Set environment variables to use the venv
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "-m", "bot.bot"]

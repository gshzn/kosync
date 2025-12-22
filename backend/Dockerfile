FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV UV_NO_DEV=1

# Copy dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --locked

# Copy the client binary
# Ensure this file exists in your backend root before building
COPY kosync_client /app/kosync_client

# Copy application code
COPY . .

# Expose the port
EXPOSE 8000

# Run the application
CMD ["uv", "run", "uvicorn", "kosync_backend.main:get_app", "--factory", "--proxy-headers"]


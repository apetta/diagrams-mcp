# Dockerfile for Diagrams MCP Server

# Use official uv Docker image with Python 3.12 on Debian
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install Graphviz (system dependency for diagrams library)
RUN apt-get update && \
    apt-get install -y graphviz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Enable bytecode compilation for faster startup
ENV UV_COMPILE_BYTECODE=1

# Copy from cache instead of linking (required for Docker volumes)
ENV UV_LINK_MODE=copy

# Copy pyproject file for diagrams-mcp
COPY pyproject_diagrams.toml pyproject.toml

# Install project dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-install-project --no-dev

# Copy application code
COPY src/diagrams_mcp /app/src/diagrams_mcp

# Install the application itself
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --no-dev

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"

# Reset entrypoint (don't invoke uv wrapper)
ENTRYPOINT []

# Expose port 8081 (Smithery standard)
EXPOSE 8081

# Run the HTTP server
# Note: The PORT environment variable is set by Smithery to 8081
CMD ["python", "-m", "diagrams_mcp.http_server"]

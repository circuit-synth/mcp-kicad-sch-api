FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy all files needed for installation
COPY pyproject.toml README.md ./
COPY src/ src/

# Install the package
RUN pip install --no-cache-dir -e .

# Create non-root user
RUN adduser --disabled-password --gecos '' mcpuser
USER mcpuser

# Expose port for HTTP transport (optional)
EXPOSE 8000

# Default to stdio transport
CMD ["python", "-m", "mcp_kicad_sch_api"]
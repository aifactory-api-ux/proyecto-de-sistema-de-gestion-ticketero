# Simple static frontend Dockerfile using Python http.server
# Multi-stage build not needed for static files

FROM python:3.11-slim

# Create non-root user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Set working directory
WORKDIR /app

# Copy static frontend files
COPY index.html ./
COPY main.js ./

# Set ownership
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check (handled by docker-compose)

# Startup command: serve static files on 0.0.0.0:8080
CMD ["python", "-m", "http.server", "8080", "--bind", "0.0.0.0"]

FROM python:3.11-slim

# Create a non-root user for security
RUN groupadd -r ecodna && useradd -r -g ecodna ecodna

# Set the working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend build artifacts
COPY frontend/dist ./frontend/dist

# Copy the rest of the application code
COPY . .

# Change ownership to non-root user
RUN chown -R ecodna:ecodna /app

# Switch to non-root user
USER ecodna

# Expose the port the app runs on (Cloud Run provides the PORT env var)
ENV PORT=8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT}/health')" || exit 1

# Run the FastAPI application using uvicorn
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]

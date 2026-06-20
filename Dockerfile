FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the frontend build artifacts
COPY frontend/dist ./frontend/dist

# Copy the rest of the application code
COPY . .

# Expose the port the app runs on (Cloud Run provides the PORT env var)
ENV PORT=8080

# Run the FastAPI application using uvicorn
CMD ["sh", "-c", "uvicorn api:app --host 0.0.0.0 --port ${PORT}"]

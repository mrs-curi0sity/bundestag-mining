# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary source files
COPY src/ ./src/
COPY dashboard/ ./dashboard/

# Copy only the data you need
COPY data/2025/output/ ./data/2025/output/

# Create non-root user
RUN useradd -m dashuser && chown -R dashuser:dashuser /app

# Switch to non-root user
USER dashuser

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "dashboard/abgeordneten-dashboard.py"]
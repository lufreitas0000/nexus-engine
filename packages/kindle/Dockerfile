FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pandoc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories for artifacts and uploads
RUN mkdir -p artifacts temp_upload

# Copy the rest of the application
# Ensure you clone with submodules recursively when building this
COPY . .

# Expose port for Streamlit
EXPOSE 8501

# Run the Streamlit application
CMD ["streamlit", "run", "src/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

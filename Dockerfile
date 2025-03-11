# book-lending-prototype/Dockerfile
FROM ubuntu:24.04
WORKDIR /app

# Update package lists and install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip3 install --break-system-packages -r requirements.txt

# Copy frontend package files and install Node.js dependencies
COPY frontend/package.json frontend/package-lock.json* ./frontend/
RUN cd frontend && npm install && cd ..

# Copy application code
COPY app/ ./app/
COPY frontend/ ./frontend/

# Default command (overridden in docker-compose.yml)
CMD ["bash"]
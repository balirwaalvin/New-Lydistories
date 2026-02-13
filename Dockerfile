FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY server/requirements.txt server/requirements.txt
RUN pip install --no-cache-dir -r server/requirements.txt

# Install Node dependencies and build React
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Expose port
EXPOSE 8080

# Run Flask via gunicorn
WORKDIR /app/server
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8080", "--workers", "2"]

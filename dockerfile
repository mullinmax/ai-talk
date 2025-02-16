FROM python:3.9-slim

# Install Node.js
RUN apt-get update && \
    apt-get install -y curl gnupg && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Create a working directory
WORKDIR /app

# Copy Node dependencies and install
COPY src/package*.json ./src/
RUN cd src && npm install

# Copy Python dependencies and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose ports
EXPOSE 3000
EXPOSE 8000

# Start both servers
CMD ["/bin/sh", "-c", "cd src && npm start & uvicorn app.main:app --host 0.0.0.0 --port 8000"]

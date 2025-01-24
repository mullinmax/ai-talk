# Use a lightweight Python base image
FROM python:3.9-slim

# Create a working directory
WORKDIR /app

# Copy the requirements file first to leverage Docker's caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of our code
COPY . .

# Expose port 80 (or 8000) for FastAPI
EXPOSE 80

# Run the app with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

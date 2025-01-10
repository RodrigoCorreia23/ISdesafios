# Base image
FROM python:3.10-slim

# Instalar ferramentas necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the gRPC port
EXPOSE 50051

# Start the gRPC server
CMD ["python", "main.py"]

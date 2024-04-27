# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for Kafka and Time Series (optional)
ENV KAFKA_BOOTSTRAP_SERVERS=kafka.default.svc.cluster.local:9092
# Add other environment variables as needed

# Run the FastAPI app
CMD ["uvicorn", "simulator:app", "--host", "0.0.0.0", "--port", "8000"]
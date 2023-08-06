#!/bin/bash

# Get the folder name as input
read -p "Enter the project name: " proj_name

# Create the main project directory
mkdir "$proj_name"
cd "$proj_name"

# Create the src directory to contain the application code
mkdir -p src

# Create the tests directory to contain the test code
mkdir -p test

# Create additional standard directories and files
touch README.md
touch requirements.txt

# Create the Dockerfile and populate it with the appropriate content
cat <<EOT >Dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install the required packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable for Python
ENV PYTHONUNBUFFERED 1

# Run the main.py file when the container launches
CMD ["python", "src/$proj_name/app/main.py"]
EOT

# Inside the src directory, you can create subdirectories for your application
cd src
mkdir -p "$proj_name"
cd "$proj_name"

# Create folders for FastAPI application
mkdir -p api
mkdir -p app
mkdir -p core

# Create the main FastAPI app file and populate it with the template content
cat <<EOT >app/main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "FastAPI"}
EOT

# Create the FastAPI router and endpoint files and populate them with the template content
cat <<EOT >src/"$proj_name"/api/api_v1.py
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_root():
    return {"Hello": "FastAPI"}
EOT

# Print the structure to verify
echo "Created folder structure:"
tree ../../../

# Go back to the original directory
cd ../../../

echo "Folder structure created successfully!"

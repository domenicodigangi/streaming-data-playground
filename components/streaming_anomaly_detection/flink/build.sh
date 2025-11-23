#!/bin/bash
# Build script for Flink Streaming Anomaly Detection Job

set -e

echo "Building Flink Streaming Anomaly Detection JAR..."
echo "=================================================="

cd "$(dirname "$0")/streamingad"

# Check if Maven is available
if ! command -v mvn &> /dev/null; then
    echo "Error: Maven is not installed. Please install Maven 3.6+ to build the project."
    echo "Alternative: Use 'docker-compose up --build' which builds the JAR automatically."
    exit 1
fi

# Build the JAR
echo "Running Maven build..."
mvn clean package -DskipTests

# Check if build was successful
if [ -f "target/streamingad-0.1-SNAPSHOT.jar" ]; then
    echo ""
    echo "✓ Build successful!"
    echo "  JAR location: $(pwd)/target/streamingad-0.1-SNAPSHOT.jar"
    echo "  Size: $(du -h target/streamingad-0.1-SNAPSHOT.jar | cut -f1)"
else
    echo "✗ Build failed! JAR not found."
    exit 1
fi

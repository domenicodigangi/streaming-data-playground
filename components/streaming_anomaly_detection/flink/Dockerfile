# Multi-stage build for Flink job with embedded JAR
FROM maven:3.8-openjdk-11 AS builder

# Copy the Flink project
COPY streamingad /app
WORKDIR /app

# Build the JAR
RUN mvn clean package -DskipTests

# Runtime stage
FROM flink:1.18

# Copy the built JAR to Flink's lib directory
COPY --from=builder /app/target/streamingad-0.1-SNAPSHOT.jar /opt/flink/usrlib/job.jar

# Copy configuration
COPY streamingad/src/main/resources/kafka-config-for-compose.properties /opt/flink/conf/kafka-config.properties

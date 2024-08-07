# Stage 1: Build the Flink job using Maven
FROM   flink:1.18.1
# Set the working directory inside the container
WORKDIR /app

# Copy the Maven project files to the container
COPY pom.xml ./
COPY src ./src

# Compile the Maven project and package it as a JAR file
RUN mvn clean package

# Stage 2: Run the Flink job in local mode
FROM flink:1.18-scala_2.12

# Set the working directory inside the container
WORKDIR /opt/flink

# Copy the JAR file from the build stage to the Flink container
COPY --from=build /app/target/your-flink-job.jar /opt/flink/job.jar

# Set the entry point to run the Flink job in local mode
ENTRYPOINT ["flink", "run", "-c", "com.your.package.MainClass", "job.jar"]

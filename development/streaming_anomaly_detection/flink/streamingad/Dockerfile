FROM maven:3.6.3-jdk-11 AS build

WORKDIR /app
COPY pom.xml ./
COPY src ./src
RUN mvn clean package
RUN ls -l /app/target

FROM flink:1.18

WORKDIR /opt/flink
COPY --from=build /app/target/streamingad-0.1-SNAPSHOT.jar /opt/flink/job.jar
COPY /src/main/resources/ /opt/flink/src/main/resources/
ENTRYPOINT ["flink", "run", "-c", "org.streamingad.StreamingADJob", "job.jar"]

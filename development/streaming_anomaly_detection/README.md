# Real-Time Anomaly Detection on Streaming Data

This Streamlit app demonstrates a real-time anomaly detection system that uses simulated data processed by Apache Flink
and visualized using Plotly. The app interacts with a Kafka stream to display both incoming data and detected anomalies.

## Overview

### Components:

1. **Data Simulator**: Generates and streams data into a Kafka topic.
2. **Apache Flink**: Processes the streamed data to detect anomalies.
3. **Streamlit Interface**: Displays real-time data and anomaly scores, allowing user interaction. Using Redis under the
   hood to cache data between streamlit refreshes.

### How It Works:

- **Data Streaming**: Simulated data is published to Kafka topics.
- **Flink Processing**: Data is consumed by Apache Flink, which performs anomaly detection and outputs the results to
  another Kafka topic.
- **Streamlit Visualization**: The app fetches data from Kafka, caches it in Redis, and updates live charts showing the
  input data and corresponding anomaly scores.

### Features:

- **Real-Time Charts**: Continuously updated plots of streaming data and anomaly scores.
- **Historical Data Viewing**: Option to load and view historical data from Kafka.
- **Customizable**: Adjust the amount of historical data fetched and toggle live data display.

## Usage

1. **Live Data**: Toggle "Live data" to start or stop real-time updates.
2. **Reset Cache**: Clear all cached data using the "Reset" button.
3. **View History**: Set the cache to display historical data by adjusting the slider for the number of historical
   messages.
4. **Streaming Data Table**: Optionally display the raw streaming data in table format.

## Example Plots

### Input Data Stream

![Input Data Stream](input_data_stream.png)

### Anomaly Score

![Anomaly Score](anomaly_score.png)

For more details and to run this project, visit
the [GitHub repository](https://github.com/domenicodigangi/streaming-data-playground/tree/main/development/flink/streamingad).

---

These images should be saved in the directory with the README, or the links should be updated to point to where the
images are hosted if they are stored elsewhere.
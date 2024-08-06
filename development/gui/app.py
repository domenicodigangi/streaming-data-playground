import asyncio
import json
import logging
import pickle
from typing import Dict

import altair as alt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from kafka import KafkaConsumer, TopicPartition
from redislite import Redis

logger = logging.getLogger(__name__)

st.title("Real Time Anomaly Detection on Streaming Data")


def get_redis_connection() -> Redis:
    if "redis_connection" not in st.session_state:
        st.session_state.redis_connection = Redis('/tmp/redis.db')
    return st.session_state.redis_connection


def get_streaming_data_df(name: str) -> pd.DataFrame:
    redis_connection = get_redis_connection()
    pickled_df = redis_connection.get(name)
    if pickled_df is None:
        set_streaming_data_df(name, pd.DataFrame())
        return pd.DataFrame()
    return pickle.loads(pickled_df)


def set_streaming_data_df(name: str, df: pd.DataFrame):
    redis_connection = get_redis_connection()
    redis_connection.set(name, pickle.dumps(df))


def get_cached_consumer(input_topic_name: str) -> KafkaConsumer:
    key = f"consumer_{input_topic_name}"
    if key not in st.session_state:
        st.session_state[key] = get_consumer()
        st.session_state[key].subscribe([input_topic_name])

    return st.session_state[key]


def get_consumer(**kwargs) -> KafkaConsumer:
    return KafkaConsumer(bootstrap_servers=st.secrets["BOOTSTRAP_URL"], **kwargs)


def fetch_new_data_from_kafka(topic: str) -> pd.DataFrame:
    consumer = get_cached_consumer(topic)
    poll_res = consumer.poll(max_records=1000, timeout_ms=1000)
    return poll_res_to_df(poll_res)


def poll_res_to_df(poll_res: Dict) -> pd.DataFrame:
    if poll_res is None or len(poll_res.keys()) == 0:
        return pd.DataFrame()
    if len(poll_res.keys()) != 1:
        raise ValueError(f"Expected 1 topic partition, got {len(poll_res.keys())}")
    topic_partition = list(poll_res.keys())[0]
    msgs = poll_res[topic_partition]
    records = [json.loads(msg.value) for msg in msgs]
    new_data = pd.DataFrame.from_records(records)
    new_data['timestamp'] = pd.to_datetime(new_data['timestamp'], unit='ms')
    new_data = new_data.set_index('timestamp')
    return new_data


def fetch_historical_data_from_kafka(topic: str, len_hist: int,
                                     max_records: int = 200) -> pd.DataFrame:
    consumer = get_consumer()
    partition = 0  # Assuming a single partition. Adjust as needed.
    tp = TopicPartition(topic, partition)
    consumer.assign([tp])
    end_offset = consumer.end_offsets([tp])[tp]
    start_offset = max(end_offset - len_hist, 0)
    consumer.seek(tp, start_offset)
    st.write(f"Fetching historical data from {start_offset} to {end_offset}")
    df = pd.DataFrame()
    poll_res = consumer.poll(max_records=max_records, timeout_ms=1000)
    while poll_res[tp][-1].offset < end_offset:
        poll_res = consumer.poll(max_records=max_records, timeout_ms=1000)
        df = pd.concat([df, poll_res_to_df(poll_res)])
    consumer.close()
    df = df.sort_values('timestamp')
    return df


async def input_data_chart():
    st.session_state.fragment_runs += 1
    input_topic_name = "streamingad_simulated_data"
    st.write(f"New data received from {input_topic_name} (refreshed "
             f"{st.session_state.fragment_runs} times)")

    new_data = fetch_new_data_from_kafka(input_topic_name)
    st.dataframe(new_data)
    in_data = get_streaming_data_df(input_topic_name)
    in_data = pd.concat([in_data, new_data])
    set_streaming_data_df(input_topic_name, in_data)
    st.session_state.minutes_to_show = st.slider("Minutes to show", 1, 60, 10)
    plot_data = in_data.last(f"{st.session_state.minutes_to_show}min").reset_index()
    plot_timeseries_plotly(plot_data)


def plot_timeseries_plotly(df_to_plot: pd.DataFrame):
    fig = go.Figure([go.Scatter(x=df_to_plot['timestamp'], y=df_to_plot['value'])])
    st.plotly_chart(fig, use_container_width=True)


def plot_timeseries_altair(df_to_plot: pd.DataFrame):
    chart = alt.Chart(df_to_plot).mark_line().encode(x='timestamp:T', y='value', )
    st.altair_chart(chart, theme=None, use_container_width=True)


st.markdown(
    "First, data is simulated and streamed into a Kafka topic located. Next, the data "
    "is processed in Flink .")

st.markdown(
    "For more background on this project and to run it for yourself, visit the [GitHub "
    "repository](https://github.com/domenicodigangi/streaming-data-playground/tree/main"
    "/development/flink/streamingad).")

if "app_runs" not in st.session_state:
    st.session_state.app_runs = 0
    st.session_state.fragment_runs = 0


@st.fragment(run_every=0.2)
def refreshing_fragment():
    asyncio.run(input_data_chart())


def clear_all_cache():
    st.session_state.clear()
    conn = get_redis_connection()
    conn.flushdb()


def set_cache_to_history(len_hist: int):
    input_topic_name = "streamingad_simulated_data"
    historical_data = fetch_historical_data_from_kafka(input_topic_name, len_hist)
    st.write("Setting cache to historical data")
    set_streaming_data_df(f"{input_topic_name}", historical_data)


with st.sidebar:
    st.button("Reset", on_click=clear_all_cache)
    len_hist = st.slider(label="N messages from history", min_value=1_000,
                         max_value=10_000, value=500, step=500)
    if st.button("Set cache to history"):
        set_cache_to_history(len_hist)

live = st.toggle("Live data", True)
if live:
    refreshing_fragment()
else:
    asyncio.run(input_data_chart())

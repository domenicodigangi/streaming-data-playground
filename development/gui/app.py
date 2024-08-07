import asyncio
import json
import logging
import pickle
from typing import Dict

import altair as alt
import httpx
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from kafka import KafkaConsumer, TopicPartition
from redislite import Redis

logger = logging.getLogger(__name__)


@st.cache_resource
def get_redis_connection() -> Redis:
    return Redis('/tmp/redis.db')


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


@st.cache_resource
def get_cached_consumer(topic_name: str) -> KafkaConsumer:
    key = f"consumer_{topic_name}"
    st.session_state[key] = get_consumer()
    st.session_state[key].subscribe([topic_name])
    return st.session_state[key]


def get_consumer(**kwargs) -> KafkaConsumer:
    return KafkaConsumer(bootstrap_servers=st.secrets["BOOTSTRAP_URL"], **kwargs)


def fetch_new_data_from_kafka(topic: str) -> pd.DataFrame:
    consumer = get_cached_consumer(topic)
    poll_res = consumer.poll(max_records=1000, timeout_ms=1000)
    return poll_res_to_df(poll_res)


def poll_res_to_df(poll_res: Dict, time_col: str = "timestamp") -> pd.DataFrame:
    if poll_res is None or len(poll_res.keys()) == 0:
        return pd.DataFrame()
    if len(poll_res.keys()) != 1:
        raise ValueError(f"Expected 1 topic partition, got {len(poll_res.keys())}")
    topic_partition = list(poll_res.keys())[0]
    msgs = poll_res[topic_partition]
    records = [json.loads(msg.value) for msg in msgs]
    new_data = pd.DataFrame.from_records(records)
    new_data[time_col] = pd.to_datetime(new_data[time_col], unit='ms')
    new_data = new_data.set_index(time_col)
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


async def streaming_charts():
    # await input_data_chart()
    st.session_state["min_to_show"] = st.slider(f"Minutes to show", 1, 60, 10)
    await kafka_streaming_chart("streamingad_simulated_data", "value", "Input data",
                                st.session_state["min_to_show"])
    await kafka_streaming_chart("streamingad_output", "score_ad", "Anomaly score",
                                st.session_state["min_to_show"])


async def input_data_chart():
    topic_name = "streamingad_simulated_data"
    new_data = fetch_new_data_from_kafka(topic_name)
    st.dataframe(new_data)
    in_data = get_streaming_data_df(topic_name)
    in_data = pd.concat([in_data, new_data])
    set_streaming_data_df(topic_name, in_data)
    st.session_state.minutes_to_show = st.slider("Minutes to show", 1, 60, 10)
    plot_data = in_data.last(f"{st.session_state.minutes_to_show}min").reset_index()
    plot_timeseries_plotly(plot_data, "value", "Input data")


async def kafka_streaming_chart(topic_name: str, y_col: str, title: str, last_n_min: int):
    new_data = fetch_new_data_from_kafka(topic_name)
    chart_key = f"show_data_{topic_name}_{title}"

    in_data = get_streaming_data_df(topic_name)
    in_data = pd.concat([in_data, new_data])
    set_streaming_data_df(topic_name, in_data)

    plot_data = in_data.last(f"{last_n_min} min").reset_index()
    plot_timeseries_plotly(plot_data, y_col, title)
    st.toggle("Show Streaming Data as table", key=chart_key)

    if st.session_state[chart_key]:
        st.dataframe(new_data)


def plot_timeseries_plotly(df_to_plot: pd.DataFrame, y_col: str, title: str,
                           x_col: str = "timestamp", ):
    fig = go.Figure([go.Scatter(x=df_to_plot[x_col], y=df_to_plot[y_col])])
    fig.update_layout(title=title)
    st.plotly_chart(fig, use_container_width=True)


def plot_timeseries_altair(df_to_plot: pd.DataFrame):
    chart = alt.Chart(df_to_plot).mark_line().encode(x='timestamp:T', y='value', )
    st.altair_chart(chart, theme=None, use_container_width=True)


@st.fragment(run_every=0.2)
def refreshing_fragment():
    asyncio.run(streaming_charts())


def clear_all_cache():
    st.session_state.clear()
    conn = get_redis_connection()
    conn.flushdb()


def set_cache_to_history(len_hist: int):
    topic_name = "streamingad_simulated_data"
    historical_data = fetch_historical_data_from_kafka(topic_name, len_hist)
    st.write("Setting cache to historical data")
    set_streaming_data_df(f"{topic_name}", historical_data)


def simulator_settings():
    st.session_state.simulator_msgs_per_sec = st.slider("Number of messages per second",
                                                        1, 100, 10)
    st.session_state.simulator_mean = st.slider("Mean", 0, 10, 1)
    st.session_state.simulator_variance = st.slider("Variance", 0, 10, 1)


def update_gaussian_sampler_simulator_settings():
    base_url = get_base_simulator_url()
    update_url = f"{base_url}/gaussian/gaussian_sampler/update"
    interval_sec = 1 / st.session_state.simulator_msgs_per_sec
    response = httpx.post(update_url, json={"mean": st.session_state.simulator_mean,
                                            "variance": 
                                                st.session_state.simulator_variance,
                                            "interval_sec": interval_sec})


def stop_gaussian_sampler():
    base_url = get_base_simulator_url()
    stop_url = f"{base_url}/gaussian/gaussian_sampler/stop"
    response = httpx.post(stop_url)
    return response


@st.cache_data
def get_base_simulator_url():
    return f"http://{st.secrets['SIMULATOR_HOST']}:{st.secrets['SIMULATOR_PORT']}/v1"


st.title("Real Time Anomaly Detection on Streaming Data")

st.markdown(
    "First, data is simulated and streamed into a Kafka topic located. Next, the data "
    "is processed in Flink .")

st.markdown(
    "For more background on this project and to run it for yourself, visit the [GitHub "
    "repository](https://github.com/domenicodigangi/streaming-data-playground/tree/main"
    "/development/flink/streamingad).")

with st.sidebar:
    st.button("Reset", on_click=clear_all_cache)
    len_hist = st.slider(label="N messages from history", min_value=1_000,
                         max_value=10_000, value=500, step=500)
    if st.button("Set cache to history"):
        set_cache_to_history(len_hist)

    st.header("Simulator settings")
    simulator_settings()
    col_1, col_2 = st.columns(2)
    with col_1:
        if st.button("Start/Update simulator"):
            update_gaussian_sampler_simulator_settings()
    with col_2:
        if st.button("Stop simulator"):
            stop_gaussian_sampler()

col_1, col_2 = st.columns(2)
with col_1:
    live = st.toggle("Live data", True)
with col_2:
    st.button("Refresh")

if live:
    refreshing_fragment()
else:
    asyncio.run(streaming_charts())

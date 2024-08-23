import logging

import httpx
import streamlit as st

logger = logging.getLogger(__name__)


class SimulatorHelper:
    def __init__(self, source_id:int = 0):
        self.source_id = source_id
    def show_simulator_tuning(self):
        st.header("Simulator settings")
        self.show_simulator_settings()
        col_1, col_2 = st.columns(2)
        with col_1:
            if st.button("Start/Update simulator"):
                self.update_gaussian_sampler_simulator_settings()
        with col_2:
            if st.button("Stop simulator"):
                self.stop_gaussian_sampler()

    def show_simulator_settings(self):
        st.session_state.simulator_msgs_per_sec = st.slider(
            "Number of messages per second", 1, 100, 10)
        st.session_state.simulator_mean = st.slider("Mean", 0, 10, 1)
        st.session_state.simulator_variance = st.slider("Variance", 0, 10, 1)

    def update_gaussian_sampler_simulator_settings(self):
        base_url = self.get_base_simulator_url()
        update_url = f"{base_url}/{self.source_id}/update"
        interval_sec = 1 / st.session_state.simulator_msgs_per_sec
        response = httpx.post(update_url, json=
        {
            "sampler_id": self.source_id,
            "mean": st.session_state.simulator_mean,
            "variance": st.session_state.simulator_variance,
            "interval_sec": interval_sec
        }
                              )

    def stop_gaussian_sampler(self):
        base_url = self.get_base_simulator_url()
        stop_url = f"{base_url}/{self.source_id}/stop"
        response = httpx.post(stop_url)
        return response

    def get_base_simulator_url(self):
        return get_base_simulator_url()


@st.cache_data
def get_base_simulator_url():
    return f"http://{st.secrets['SIMULATOR_HOST']}:{st.secrets['SIMULATOR_PORT']}/v1/gaussian/gaussian_sampler"

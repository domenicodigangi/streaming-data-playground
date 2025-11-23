#!/usr/bin/env python3
"""
Demo script for Real-Time Anomaly Detection System

This script demonstrates the key features of the anomaly detection pipeline
by programmatically controlling the data simulator and injecting anomalies.

Usage:
    python demo.py [--duration SECONDS]

Requirements:
    - Docker Compose running (docker-compose up)
    - Python 3.7+
    - requests library (pip install requests)
"""

import argparse
import sys
import time
from typing import List

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found. Install with: pip install requests")
    sys.exit(1)


class DataSimulatorClient:
    """Client for interacting with the Data Simulator API."""

    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = requests.Session()

    def health_check(self) -> bool:
        """Check if the simulator API is responsive."""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Health check failed: {e}")
            return False

    def start_sampler(
        self, sampler_id: str, mean: float = 5.0, variance: float = 1.0, interval_sec: float = 0.1
    ) -> dict:
        """Start a new Gaussian sampler."""
        url = f"{self.base_url}/v1/gaussian/gaussian_sampler/start/{sampler_id}"
        payload = {"mean": mean, "variance": variance, "interval_sec": interval_sec}
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def update_sampler(self, sampler_id: str, **kwargs) -> dict:
        """Update parameters of a running sampler."""
        url = f"{self.base_url}/v1/gaussian/{sampler_id}/update"
        response = self.session.post(url, json=kwargs)
        response.raise_for_status()
        return response.json()

    def inject_anomaly(self, sampler_id: str, values: List[float], n_observations: int) -> dict:
        """Inject an anomaly pattern."""
        url = f"{self.base_url}/v1/gaussian/{sampler_id}/anomaly"
        payload = {"values": values, "n_observations": n_observations}
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def stop_sampler(self, sampler_id: str) -> dict:
        """Stop a running sampler."""
        url = f"{self.base_url}/v1/gaussian/{sampler_id}/stop"
        response = self.session.post(url)
        response.raise_for_status()
        return response.json()


def print_banner(text: str):
    """Print a formatted banner."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def wait_with_message(seconds: int, message: str):
    """Wait with a countdown message."""
    print(f"{message} ({seconds}s)")
    for i in range(seconds, 0, -1):
        print(f"  {i}s remaining...", end="\r")
        time.sleep(1)
    print("  Done!          ")


def run_demo(client: DataSimulatorClient, duration_multiplier: float = 1.0):
    """Run the complete demo sequence."""

    sampler_id = "demo_sensor"

    try:
        print_banner("Real-Time Anomaly Detection Demo")
        print("📊 Dashboard: http://localhost:8501")
        print("🔧 Flink UI:  http://localhost:8081")
        print("📡 API Docs:  http://localhost:8001/docs\n")

        # Step 1: Start sampler
        print_banner("Step 1: Starting Data Generation")
        print(f"Starting sampler '{sampler_id}' with normal distribution (mean=5.0, variance=1.0)")
        result = client.start_sampler(sampler_id, mean=5.0, variance=1.0, interval_sec=0.1)
        print(f"✓ Sampler started: {result.get('status', 'unknown')}")

        # Step 2: Establish baseline
        print_banner("Step 2: Establishing Baseline")
        wait_with_message(int(30 * duration_multiplier), "Generating normal data for baseline")

        # Step 3: Spike anomaly
        print_banner("Step 3: Injecting Spike Anomaly")
        print("Injecting a sudden spike anomaly...")
        spike_values = [0, 0, 0, 5, 10, 20, 30, 20, 10, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        result = client.inject_anomaly(sampler_id, spike_values, n_observations=50)
        print(f"✓ Spike anomaly injected: {result.get('anomaly_duration_samples', 50)} samples")
        print("👀 Watch the dashboard for the red anomaly spike!")
        wait_with_message(int(20 * duration_multiplier), "Observing spike anomaly")

        # Step 4: Return to normal
        print_banner("Step 4: Returning to Normal")
        wait_with_message(int(15 * duration_multiplier), "Anomaly completed, back to normal")

        # Step 5: Gradual drift
        print_banner("Step 5: Injecting Gradual Drift Anomaly")
        print("Injecting a gradual upward drift...")
        drift_values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        result = client.inject_anomaly(sampler_id, drift_values, n_observations=100)
        print(f"✓ Drift anomaly injected: {result.get('anomaly_duration_samples', 100)} samples")
        print("👀 Watch the dashboard for gradual anomaly score increase!")
        wait_with_message(int(30 * duration_multiplier), "Observing drift anomaly")

        # Step 6: Adjust variance
        print_banner("Step 6: Demonstrating Parameter Adjustment")
        print("Increasing variance to make data noisier...")
        result = client.update_sampler(sampler_id, variance=3.0)
        print("✓ Variance increased to 3.0")
        wait_with_message(int(15 * duration_multiplier), "Observing increased noise")

        print("Decreasing variance for stable data...")
        result = client.update_sampler(sampler_id, variance=0.5)
        print("✓ Variance decreased to 0.5")
        wait_with_message(int(15 * duration_multiplier), "Observing stable data")

        # Step 7: Cleanup
        print_banner("Step 7: Demo Complete")
        print(f"Stopping sampler '{sampler_id}'...")
        result = client.stop_sampler(sampler_id)
        print(f"✓ Sampler stopped: {result.get('status', 'unknown')}")

        print_banner("🎉 Demo Complete!")
        print("Key Observations:")
        print("  • Spike anomalies show sharp increases in anomaly score")
        print("  • Gradual drifts are detected over time")
        print("  • Parameter changes affect data distribution")
        print("  • Each source_id has independent anomaly detection")
        print("\nNext Steps:")
        print("  • Explore the Streamlit dashboard for interactive controls")
        print("  • Try the API at http://localhost:8001/docs")
        print("  • Read QUICKSTART.md for more examples")
        print("  • Check README.md for full documentation")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error communicating with API: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure docker-compose is running: docker-compose ps")
        print("  2. Check API health: curl http://localhost:8001/health")
        print("  3. View logs: docker-compose logs data-simulator")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        print(f"Cleaning up: stopping sampler '{sampler_id}'...")
        try:
            client.stop_sampler(sampler_id)
            print("✓ Sampler stopped")
        except:
            print("⚠️  Could not stop sampler (may already be stopped)")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        description="Demo script for Real-Time Anomaly Detection System"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=1.0,
        help="Duration multiplier (default: 1.0, use 0.5 for faster demo)",
    )
    parser.add_argument(
        "--url", type=str, default="http://localhost:8001", help="API base URL"
    )
    args = parser.parse_args()

    client = DataSimulatorClient(base_url=args.url)

    # Health check
    print("Checking API health...", end=" ")
    if not client.health_check():
        print("❌ FAILED")
        print("\nError: Cannot connect to Data Simulator API")
        print(f"  URL: {args.url}")
        print("\nTroubleshooting:")
        print("  1. Start the system: docker-compose up")
        print("  2. Wait for services to be ready (~2-3 minutes)")
        print("  3. Check service status: docker-compose ps")
        print("  4. View logs: docker-compose logs")
        sys.exit(1)
    print("✓ OK")

    # Run demo
    run_demo(client, duration_multiplier=args.duration)


if __name__ == "__main__":
    main()

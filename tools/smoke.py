"""Check a running leaf API with a real image and an expected model version."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import httpx2 as httpx


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE = ROOT / "data" / "current" / "leaf-01.jpg"
DEFAULT_VERSION = "phase1-reference-v1"
LABELS = ("angular_leaf_spot", "bean_rust", "healthy")


def response_body(response: httpx.Response, endpoint: str) -> dict:
    if response.status_code != 200:
        raise ValueError(f"{endpoint} returned HTTP {response.status_code}, expected 200")
    try:
        payload = response.json()
    except ValueError as exc:
        raise ValueError(f"{endpoint} returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{endpoint} did not return a JSON object")
    return payload


def wait_for_ready(client: httpx.Client, wait_seconds: int) -> dict:
    deadline = time.monotonic() + wait_seconds
    while True:
        try:
            response = client.get("/ready")
        except httpx.TransportError as exc:
            reason = str(exc) or type(exc).__name__
        else:
            if response.status_code not in (502, 503, 504):
                payload = response_body(response, "GET /ready")
                if payload.get("status") != "ready":
                    raise ValueError("GET /ready did not report status 'ready'")
                return payload
            reason = f"HTTP {response.status_code}"
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise ValueError(f"GET /ready did not become ready ({reason})")
        time.sleep(min(2.0, remaining))


def run_smoke(url: str, image: Path, expected_version: str, wait_seconds: int) -> None:
    if not image.is_file():
        raise ValueError(f"Image file not found: {image}")

    with httpx.Client(base_url=url, timeout=10.0) as client:
        ready = wait_for_ready(client, wait_seconds)
        ready_version = ready.get("model_version")
        if ready_version != expected_version:
            raise ValueError(
                f"GET /ready reported model version {ready_version!r}, "
                f"expected {expected_version!r}"
            )
        print(f"PASS GET /ready (model_version={ready_version})")

        health = response_body(client.get("/health"), "GET /health")
        if health.get("status") != "ok":
            raise ValueError("GET /health did not report status 'ok'")
        print("PASS GET /health")

        with image.open("rb") as image_file:
            response = client.post("/predict", files={"file": (image.name, image_file)})

    prediction = response_body(response, "POST /predict")
    actual_version = prediction.get("model_version")
    if actual_version != expected_version:
        raise ValueError(
            f"POST /predict reported model version {actual_version!r}, "
            f"expected {expected_version!r}"
        )
    label = prediction.get("label")
    if label not in LABELS:
        raise ValueError(f"POST /predict returned an unexpected label: {label!r}")
    confidence = prediction.get("confidence")
    if type(confidence) not in (int, float) or not 0 <= confidence <= 1:
        raise ValueError("POST /predict confidence must be a number between 0 and 1")
    print(f"PASS POST /predict (label={label}, model_version={actual_version})")
    print(json.dumps(prediction, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000", help="Base URL of the API")
    parser.add_argument("--image", default=DEFAULT_IMAGE, type=Path, help="Path to a leaf image")
    parser.add_argument("--expected-version", default=DEFAULT_VERSION, help="Required model version")
    parser.add_argument("--wait-seconds", default=90, type=int, help="Time to retry /ready")
    args = parser.parse_args()
    if args.wait_seconds < 0:
        parser.error("--wait-seconds must be zero or greater")

    try:
        run_smoke(args.url, args.image, args.expected_version, args.wait_seconds)
    except (httpx.HTTPError, httpx.InvalidURL, OSError, ValueError) as exc:
        print(f"FAIL {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

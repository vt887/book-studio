#!/usr/bin/env python3
import argparse
import http.client
import json
import random
import statistics
import time
from urllib import error, request


# Avoid inherited HTTP proxy settings for localhost calls.
NO_PROXY_OPENER = request.build_opener(request.ProxyHandler({}))


def post_json(url: str, payload: dict, timeout: float = 10.0, attempts: int = 4) -> tuple[float, dict]:
    data = json.dumps(payload).encode("utf-8")

    for attempt in range(1, attempts + 1):
        req = request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        t0 = time.perf_counter()
        try:
            with NO_PROXY_OPENER.open(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8")
            return (time.perf_counter() - t0) * 1000.0, json.loads(body)

        except Exception:
            # будь-яка мережна помилка = retry
            if attempt == attempts:
                raise
            time.sleep(min(2.0, 0.2 * (2 ** (attempt - 1))))


def wait_ready(base_url: str, timeout_seconds: int = 40) -> None:
    base = base_url.rstrip("/")
    ready_url = base + "/ready"
    health_url = base + "/health"
    deadline = time.time() + timeout_seconds
    last_error = None

    while time.time() < deadline:
        try:
            req = request.Request(ready_url, method="GET")
            with NO_PROXY_OPENER.open(req, timeout=3) as resp:
                payload = json.loads(resp.read().decode("utf-8"))

            status = payload.get("status")

            if status == "ready":
                return
            last_error = f"ready status={status}"

        except Exception as exc:  # noqa: BLE001
            # не валимо readiness через тимчасові фейли
            last_error = f"ready: {exc}"

        try:
            req = request.Request(health_url, method="GET")
            with NO_PROXY_OPENER.open(req, timeout=3) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            checks = payload.get("checks") or {}
            if checks.get("postgres") and checks.get("redis"):
                return
            last_error = f"health status={payload.get('status')} checks={checks}"
        except Exception as exc:  # noqa: BLE001
            last_error = f"health: {exc}"

        time.sleep(1)

    raise RuntimeError(
        f"Service not ready after {timeout_seconds}s at {base_url} "
        f"(last checked: {ready_url}, {health_url}); {last_error}"
    )


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    s = sorted(values)
    idx = int((p / 100) * (len(s) - 1))
    return s[idx]


def efficiency_percent(uncached_ms: float, cached_ms: float) -> float:
    if uncached_ms <= 0:
        return 0.0
    return ((uncached_ms - cached_ms) / uncached_ms) * 100.0


def run_cached(base_url: str, query: str, top_k: int, role: str | None, runs: int) -> list[float]:
    url = f"{base_url.rstrip('/')}/ctx/read"
    payload = {"query": query, "top_k": top_k}
    if role:
        payload["role"] = role

    post_json(url, payload)  # warm-up

    out = []
    for _ in range(runs):
        ms, _ = post_json(url, payload)
        out.append(ms)
    return out


def run_uncached(base_url: str, top_k: int, role: str | None, runs: int) -> list[float]:
    url = f"{base_url.rstrip('/')}/ctx/read"
    out = []

    for i in range(runs):
        payload = {
            "query": f"benchmark-{i}-{random.randint(1, 10_000_000)}",
            "top_k": top_k,
        }
        if role:
            payload["role"] = role

        ms, _ = post_json(url, payload)
        out.append(ms)

    return out


def print_stats(name: str, latencies: list[float]) -> None:
    if not latencies:
        print(f"{name}: no data")
        return

    print(f"{name} count={len(latencies)}")
    print(f"  mean_ms={statistics.mean(latencies):.2f}")
    print(f"  p50_ms={percentile(latencies, 50):.2f}")
    print(f"  p95_ms={percentile(latencies, 95):.2f}")
    print(f"  max_ms={max(latencies):.2f}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--base-url", default="http://localhost:8080")
    p.add_argument("--query", default="clean architecture boundaries")
    p.add_argument("--top-k", type=int, default=5)
    p.add_argument("--role", default=None)
    p.add_argument("--cached-runs", type=int, default=30)
    p.add_argument("--uncached-runs", type=int, default=30)
    p.add_argument("--ready-timeout", type=int, default=40)
    args = p.parse_args()

    wait_ready(args.base_url, args.ready_timeout)

    cached = run_cached(args.base_url, args.query, args.top_k, args.role, args.cached_runs)
    uncached = run_uncached(args.base_url, args.top_k, args.role, args.uncached_runs)

    print_stats("cached", cached)
    print_stats("uncached", uncached)

    cached_mean = statistics.mean(cached) if cached else 0.0
    uncached_mean = statistics.mean(uncached) if uncached else 0.0
    cached_p50 = percentile(cached, 50)
    uncached_p50 = percentile(uncached, 50)
    cached_p95 = percentile(cached, 95)
    uncached_p95 = percentile(uncached, 95)

    print("cache_efficiency")
    print(f"  mean_gain_pct={efficiency_percent(uncached_mean, cached_mean):.2f}%")
    print(f"  p50_gain_pct={efficiency_percent(uncached_p50, cached_p50):.2f}%")
    print(f"  p95_gain_pct={efficiency_percent(uncached_p95, cached_p95):.2f}%")

    print("targets")
    print(f"  cached_p95_lt_200ms={'PASS' if cached_p95 < 200 else 'FAIL'}")
    print(f"  uncached_p95_lt_500ms={'PASS' if uncached_p95 < 500 else 'FAIL'}")


if __name__ == "__main__":
    main()

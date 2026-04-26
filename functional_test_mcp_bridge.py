#!/usr/bin/env python3
import argparse
import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib import error, request


@dataclass
class StepResult:
    name: str
    passed: bool
    skipped: bool = False
    details: str = ""


class Logger:
    def __init__(self, log_file: str | None = None) -> None:
        self._fh = open(log_file, "a", encoding="utf-8") if log_file else None

    def close(self) -> None:
        if self._fh:
            self._fh.close()

    def _emit(self, level: str, message: str) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] [{level}] {message}"
        print(line)
        if self._fh:
            self._fh.write(line + "\n")
            self._fh.flush()

    def info(self, message: str) -> None:
        self._emit("INFO", message)

    def ok(self, message: str) -> None:
        self._emit("OK", message)

    def warn(self, message: str) -> None:
        self._emit("WARN", message)

    def err(self, message: str) -> None:
        self._emit("ERROR", message)

    def section(self, title: str) -> None:
        self._emit("INFO", f"{'=' * 20} {title} {'=' * 20}")


# Force direct local connections. urllib may inherit system/env proxy settings
# that can break localhost calls in CLI environments.
NO_PROXY_OPENER = request.build_opener(request.ProxyHandler({}))


def pretty(data: Any) -> str:
    try:
        return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True)
    except Exception:
        return str(data)


def http_json(
    logger: Logger,
    method: str,
    url: str,
    payload: dict[str, Any] | None,
    timeout: float,
    attempts: int,
) -> tuple[int, dict[str, Any], float]:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if payload is not None else {}
    last_error: Exception | None = None

    for attempt in range(1, attempts + 1):
        req = request.Request(url=url, data=data, headers=headers, method=method)
        t0 = time.perf_counter()
        try:
            with NO_PROXY_OPENER.open(req, timeout=timeout) as resp:
                body_text = resp.read().decode("utf-8")
                status_code = resp.getcode() or 0
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            try:
                body_json = json.loads(body_text) if body_text else {}
            except json.JSONDecodeError:
                body_json = {"_raw": body_text}
            return status_code, body_json, elapsed_ms
        except error.HTTPError as exc:
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            body_text = exc.read().decode("utf-8", errors="replace")
            try:
                body_json = json.loads(body_text) if body_text else {}
            except json.JSONDecodeError:
                body_json = {"_raw": body_text}
            logger.warn(
                f"HTTP {exc.code} for {method} {url} (attempt {attempt}/{attempts}, {elapsed_ms:.1f} ms)"
            )
            if attempt == attempts:
                return exc.code, body_json, elapsed_ms
            time.sleep(min(2.0, 0.2 * (2 ** (attempt - 1))))
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warn(f"Network error for {method} {url} (attempt {attempt}/{attempts}): {exc}")
            if attempt == attempts:
                break
            time.sleep(min(2.0, 0.2 * (2 ** (attempt - 1))))

    raise RuntimeError(f"Request failed: {method} {url}; last_error={last_error}")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run_step(name: str, fn, logger: Logger, results: list[StepResult]) -> Any:
    logger.section(name)
    try:
        value = fn()
        results.append(StepResult(name=name, passed=True))
        logger.ok(f"{name}: PASS")
        return value
    except AssertionError as exc:
        results.append(StepResult(name=name, passed=False, details=str(exc)))
        logger.err(f"{name}: FAIL -> {exc}")
        return None
    except Exception as exc:  # noqa: BLE001
        results.append(StepResult(name=name, passed=False, details=str(exc)))
        logger.err(f"{name}: ERROR -> {exc}")
        return None


def run_test(base_url: str, timeout: float, attempts: int, log_file: str | None) -> int:
    logger = Logger(log_file)
    results: list[StepResult] = []
    base = base_url.rstrip("/")
    suffix = str(int(time.time()))
    book_id = f"functional-test-{suffix}"
    concept_a = f"ft-{suffix}-a"
    concept_b = f"ft-{suffix}-b"
    chunk_a = f"ch-{suffix}-a"
    chunk_b = f"ch-{suffix}-b"
    query_text = f"functional test concept {suffix}"

    logger.info(f"Base URL: {base}")
    logger.info(f"Timeout: {timeout}s, Attempts per request: {attempts}")
    logger.info(
        f"Test data: book_id={book_id}, concept_a={concept_a}, concept_b={concept_b}, "
        f"chunk_a={chunk_a}, chunk_b={chunk_b}"
    )
    logger.info(f"Unique query: {query_text}")

    ready_payload: dict[str, Any] = {}

    def step_root() -> dict[str, Any]:
        status, body, elapsed = http_json(logger, "GET", f"{base}/", None, timeout, attempts)
        logger.info(f"GET / -> status={status}, elapsed_ms={elapsed:.1f}")
        logger.info(f"Body:\n{pretty(body)}")
        require(status == 200, f"Expected HTTP 200, got {status}")
        require("service" in body, "Expected key 'service' in root response")
        return body

    def step_live() -> dict[str, Any]:
        status, body, elapsed = http_json(logger, "GET", f"{base}/live", None, timeout, attempts)
        logger.info(f"GET /live -> status={status}, elapsed_ms={elapsed:.1f}")
        logger.info(f"Body:\n{pretty(body)}")
        require(status == 200, f"Expected HTTP 200, got {status}")
        require(body.get("status") == "alive", f"Expected status=alive, got {body.get('status')}")
        return body

    def step_ready() -> dict[str, Any]:
        status, body, elapsed = http_json(logger, "GET", f"{base}/ready", None, timeout, attempts)
        logger.info(f"GET /ready -> status={status}, elapsed_ms={elapsed:.1f}")
        logger.info(f"Body:\n{pretty(body)}")
        require(status == 200, f"Expected HTTP 200, got {status}")
        require("checks" in body, "Expected key 'checks' in /ready response")
        require(body.get("status") in {"ready", "not_ready"}, "Unexpected ready status")
        checks = body.get("checks") or {}
        require(bool(checks.get("postgres")), "postgres check is false")
        require(bool(checks.get("redis")), "redis check is false")
        return body

    def step_health() -> dict[str, Any]:
        status, body, elapsed = http_json(logger, "GET", f"{base}/health", None, timeout, attempts)
        logger.info(f"GET /health -> status={status}, elapsed_ms={elapsed:.1f}")
        logger.info(f"Body:\n{pretty(body)}")
        require(status == 200, f"Expected HTTP 200, got {status}")
        require("checks" in body, "Expected key 'checks' in /health response")
        checks = body.get("checks") or {}
        require(bool(checks.get("postgres")), "postgres health is false")
        require(bool(checks.get("redis")), "redis health is false")
        return body

    def step_tools() -> dict[str, Any]:
        status, body, elapsed = http_json(logger, "GET", f"{base}/mcp/tools", None, timeout, attempts)
        logger.info(f"GET /mcp/tools -> status={status}, elapsed_ms={elapsed:.1f}")
        logger.info(f"Body:\n{pretty(body)}")
        require(status == 200, f"Expected HTTP 200, got {status}")
        tools = body.get("tools") or []
        names = {tool.get("name") for tool in tools if isinstance(tool, dict)}
        require("ctx_read" in names, "ctx_read tool missing")
        require("ctx_write" in names, "ctx_write tool missing")
        require("ctx_graph_link" in names, "ctx_graph_link tool missing")
        return body

    def step_ctx_write() -> dict[str, Any]:
        payload = {
            "book_id": book_id,
            "data": {
                "concepts": [
                    {
                        "concept_id": concept_a,
                        "name": f"Functional Test Concept A {suffix}",
                        "definition": f"Used by integration test {suffix}",
                        "summary": f"First concept for read-path checks {suffix}",
                        "importance_score": 0.8,
                        "source_chunks": [chunk_a],
                        "tags": ["test", "functional"],
                        "applicable_roles": ["developer", "tester"],
                    },
                    {
                        "concept_id": concept_b,
                        "name": f"Functional Test Concept B {suffix}",
                        "definition": f"Used by graph-link test {suffix}",
                        "summary": f"Second concept for relation checks {suffix}",
                        "importance_score": 0.7,
                        "source_chunks": [chunk_b],
                        "tags": ["test", "graph"],
                        "applicable_roles": ["developer", "architect"],
                    },
                ]
            },
        }
        logger.info(f"POST /ctx/write payload:\n{pretty(payload)}")
        status, body, elapsed = http_json(logger, "POST", f"{base}/ctx/write", payload, timeout, attempts)
        logger.info(f"POST /ctx/write -> status={status}, elapsed_ms={elapsed:.1f}")
        logger.info(f"Body:\n{pretty(body)}")
        require(status == 200, f"Expected HTTP 200, got {status}")
        require(body.get("status") == "ok", f"Expected status=ok, got {body.get('status')}")
        return body

    def step_chunks_write() -> dict[str, Any]:
        payload = {
            "chunks": [
                {
                    "chunk_id": chunk_a,
                    "book_id": book_id,
                    "text_hash": f"hash-{chunk_a}",
                    "text_content": f"chunk content A {suffix}",
                },
                {
                    "chunk_id": chunk_b,
                    "book_id": book_id,
                    "text_hash": f"hash-{chunk_b}",
                    "text_content": f"chunk content B {suffix}",
                },
            ]
        }
        logger.info(f"POST /chunks/write payload:\n{pretty(payload)}")
        status, body, elapsed = http_json(logger, "POST", f"{base}/chunks/write", payload, timeout, attempts)
        logger.info(f"POST /chunks/write -> status={status}, elapsed_ms={elapsed:.1f}")
        logger.info(f"Body:\n{pretty(body)}")
        require(status == 200, f"Expected HTTP 200, got {status}")
        require(body.get("status") == "ok", f"Expected status=ok, got {body.get('status')}")
        return body

    def step_quality_consistency() -> dict[str, Any]:
        status, body, elapsed = http_json(
            logger,
            "GET",
            f"{base}/quality/consistency/{concept_a}",
            None,
            timeout,
            attempts,
        )
        logger.info(f"GET /quality/consistency/{concept_a} -> status={status}, elapsed_ms={elapsed:.1f}")
        logger.info(f"Body:\n{pretty(body)}")
        require(status == 200, f"Expected HTTP 200, got {status}")
        require("consistency_score" in body, "Expected consistency_score in quality response")
        return body

    def step_quality_evaluate() -> dict[str, Any]:
        payload = {
            "book_id": book_id,
            "concept_ids": [concept_a, concept_b],
        }
        logger.info(f"POST /quality/evaluate payload:\n{pretty(payload)}")
        status, body, elapsed = http_json(logger, "POST", f"{base}/quality/evaluate", payload, timeout, attempts)
        logger.info(f"POST /quality/evaluate -> status={status}, elapsed_ms={elapsed:.1f}")
        logger.info(f"Body:\n{pretty(body)}")
        require(status == 200, f"Expected HTTP 200, got {status}")
        require(body.get("status") == "ok", f"Expected status=ok, got {body.get('status')}")
        require(body.get("total", 0) >= 2, "Expected at least 2 evaluated concepts")
        return body

    def step_ctx_read_postgres() -> dict[str, Any]:
        payload = {"query": query_text, "top_k": 5, "role": "developer"}
        logger.info(f"POST /ctx/read payload (first read):\n{pretty(payload)}")
        status, body, elapsed = http_json(logger, "POST", f"{base}/ctx/read", payload, timeout, attempts)
        logger.info(f"POST /ctx/read (first) -> status={status}, elapsed_ms={elapsed:.1f}")
        logger.info(f"Body:\n{pretty(body)}")
        require(status == 200, f"Expected HTTP 200, got {status}")
        require(body.get("source") in {"postgres", "cache"}, "Unexpected source value")
        results = body.get("results") or []
        require(len(results) > 0, "Expected non-empty results")
        ids = {r.get("concept_id") for r in results if isinstance(r, dict)}
        require(concept_a in ids or concept_b in ids, "Expected test concept in read results")
        return body

    def step_ctx_read_cache() -> dict[str, Any]:
        payload = {"query": query_text, "top_k": 5, "role": "developer"}
        logger.info(f"POST /ctx/read payload (cache read):\n{pretty(payload)}")
        status, body, elapsed = http_json(logger, "POST", f"{base}/ctx/read", payload, timeout, attempts)
        logger.info(f"POST /ctx/read (second) -> status={status}, elapsed_ms={elapsed:.1f}")
        logger.info(f"Body:\n{pretty(body)}")
        require(status == 200, f"Expected HTTP 200, got {status}")
        require(body.get("source") == "cache", f"Expected source=cache, got {body.get('source')}")
        return body

    def step_mcp_call_ctx_read() -> dict[str, Any]:
        payload = {
            "tool": "ctx_read",
            "arguments": {"query": query_text, "top_k": 3, "role": "developer"},
        }
        logger.info(f"POST /mcp/call payload:\n{pretty(payload)}")
        status, body, elapsed = http_json(logger, "POST", f"{base}/mcp/call", payload, timeout, attempts)
        logger.info(f"POST /mcp/call -> status={status}, elapsed_ms={elapsed:.1f}")
        logger.info(f"Body:\n{pretty(body)}")
        require(status == 200, f"Expected HTTP 200, got {status}")
        require(body.get("tool") == "ctx_read", "Expected tool=ctx_read in response")
        result = body.get("result") or {}
        require("results" in result, "Expected result.results in /mcp/call response")
        return body

    def step_graph_link() -> dict[str, Any]:
        checks = ready_payload.get("checks") or {}
        if not checks.get("neo4j"):
            raise AssertionError("SKIP: neo4j is not ready")

        payload = {
            "from_id": concept_a,
            "to_id": concept_b,
            "relation": "supports",
            "weight": 0.9,
        }
        logger.info(f"POST /ctx/graph/link payload:\n{pretty(payload)}")
        status, body, elapsed = http_json(logger, "POST", f"{base}/ctx/graph/link", payload, timeout, attempts)
        logger.info(f"POST /ctx/graph/link -> status={status}, elapsed_ms={elapsed:.1f}")
        logger.info(f"Body:\n{pretty(body)}")
        require(status == 200, f"Expected HTTP 200, got {status}")
        require(body.get("status") == "ok", f"Expected status=ok, got {body.get('status')}")
        return body

    try:
        run_step("Root Endpoint", step_root, logger, results)
        run_step("Live Endpoint", step_live, logger, results)
        ready_result = run_step("Ready Endpoint", step_ready, logger, results)
        if isinstance(ready_result, dict):
            ready_payload.update(ready_result)
        run_step("Health Endpoint", step_health, logger, results)
        run_step("MCP Tools", step_tools, logger, results)
        run_step("Chunks Write", step_chunks_write, logger, results)
        run_step("CTX Write", step_ctx_write, logger, results)
        run_step("CTX Read First", step_ctx_read_postgres, logger, results)
        run_step("CTX Read Cache", step_ctx_read_cache, logger, results)
        run_step("MCP Call ctx_read", step_mcp_call_ctx_read, logger, results)
        run_step("Quality Consistency", step_quality_consistency, logger, results)
        run_step("Quality Evaluate", step_quality_evaluate, logger, results)

        logger.section("Graph Link")
        try:
            step_graph_link()
            results.append(StepResult(name="Graph Link", passed=True))
            logger.ok("Graph Link: PASS")
        except AssertionError as exc:
            msg = str(exc)
            if msg.startswith("SKIP:"):
                results.append(StepResult(name="Graph Link", passed=True, skipped=True, details=msg[5:].strip()))
                logger.warn(f"Graph Link: SKIPPED -> {msg[5:].strip()}")
            else:
                results.append(StepResult(name="Graph Link", passed=False, details=msg))
                logger.err(f"Graph Link: FAIL -> {msg}")
        except Exception as exc:  # noqa: BLE001
            results.append(StepResult(name="Graph Link", passed=False, details=str(exc)))
            logger.err(f"Graph Link: ERROR -> {exc}")

        passed = sum(1 for r in results if r.passed and not r.skipped)
        skipped = sum(1 for r in results if r.skipped)
        failed = sum(1 for r in results if not r.passed)

        logger.section("Summary")
        for r in results:
            if r.skipped:
                logger.warn(f"{r.name}: SKIPPED ({r.details})")
            elif r.passed:
                logger.ok(f"{r.name}: PASS")
            else:
                logger.err(f"{r.name}: FAIL ({r.details})")

        logger.info(f"Totals -> passed={passed}, skipped={skipped}, failed={failed}")
        return 1 if failed > 0 else 0
    finally:
        logger.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Functional test for mcp_bridge with detailed logging"
    )
    parser.add_argument("--base-url", default="http://localhost:8080")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--attempts", type=int, default=3)
    parser.add_argument("--log-file", default=None)
    args = parser.parse_args()

    code = run_test(
        base_url=args.base_url,
        timeout=args.timeout,
        attempts=args.attempts,
        log_file=args.log_file,
    )
    sys.exit(code)


if __name__ == "__main__":
    main()

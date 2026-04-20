from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


def _http_get_with_retry(
    url: str,
    *,
    retries: int,
    delay_seconds: int,
    request_timeout: int,
) -> tuple[int, dict[str, str], str]:
    last_error: str | None = None

    for attempt in range(1, retries + 1):
        request = urllib.request.Request(url, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=request_timeout) as response:
                status_code = response.getcode()
                response_headers = {k.lower(): v for k, v in response.headers.items()}
                response_body = response.read(4096).decode("utf-8", errors="replace")
                if status_code == 200:
                    return status_code, response_headers, response_body
                last_error = f"Unexpected status {status_code}"
        except urllib.error.HTTPError as exc:
            response_body = exc.read(4096).decode("utf-8", errors="replace")
            last_error = f"HTTP {exc.code}: {response_body}"
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = str(exc)

        if attempt < retries:
            print(f"Attempt {attempt}/{retries} failed for GET {url}. Retrying in {delay_seconds}s...")
            time.sleep(delay_seconds)

    raise RuntimeError(f"Request failed after {retries} attempts for GET {url}: {last_error}")


def _build_migration_state_url(backend_health_url: str) -> str:
    return f"{backend_health_url.rstrip('/')}/migration-state"


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify backend migration head alignment")
    parser.add_argument("--backend-health-url", required=True, help="Backend health endpoint URL")
    parser.add_argument(
        "--retries",
        type=int,
        default=12,
        help="Retry attempts for migration-state checks.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=int,
        default=5,
        help="Delay between retry attempts.",
    )
    parser.add_argument(
        "--request-timeout",
        type=int,
        default=8,
        help="Timeout in seconds for each migration-state request attempt.",
    )
    args = parser.parse_args()

    if args.retries < 1:
        print("Migration-state verification failed: retries must be >= 1")
        return 1

    if args.delay_seconds < 0:
        print("Migration-state verification failed: delay-seconds must be >= 0")
        return 1

    if args.request_timeout < 1:
        print("Migration-state verification failed: request-timeout must be >= 1")
        return 1

    migration_state_url = _build_migration_state_url(args.backend_health_url)

    try:
        status_code, headers, body = _http_get_with_retry(
            migration_state_url,
            retries=args.retries,
            delay_seconds=args.delay_seconds,
            request_timeout=args.request_timeout,
        )

        content_type = headers.get("content-type", "").lower()
        if "application/json" not in content_type:
            print(f"Migration-state check failed: expected application/json response, got '{content_type}'")
            return 1

        payload = json.loads(body)
        if payload.get("status") != "ok":
            print("Migration-state payload does not contain status=ok")
            return 1

        migration_state = payload.get("migration_state")
        if not isinstance(migration_state, dict):
            print("Migration-state payload does not contain migration_state object")
            return 1

        aligned = migration_state.get("aligned")
        expected_heads = migration_state.get("expected_heads")
        current_versions = migration_state.get("current_versions")

        if not isinstance(expected_heads, list) or not isinstance(current_versions, list):
            print("Migration-state payload has invalid expected_heads/current_versions values")
            return 1

        if not expected_heads:
            print("Migration-state check failed: expected_heads is empty")
            return 1

        if aligned is not True or sorted(expected_heads) != sorted(current_versions):
            print(
                "Migration-state check failed: schema is not aligned. "
                f"expected={expected_heads} current={current_versions}"
            )
            return 1

        print("Migration-state check passed")
        print(f"- endpoint: {migration_state_url}")
        print(f"- revision: {expected_heads}")
        print(f"- status: {status_code}")
        return 0

    except (ValueError, RuntimeError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"Migration-state verification failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

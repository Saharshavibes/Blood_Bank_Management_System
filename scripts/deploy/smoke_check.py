from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request


def _http_request(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
) -> tuple[int, dict[str, str], str]:
    request = urllib.request.Request(url, headers=headers or {}, data=body, method=method)
    with urllib.request.urlopen(request, timeout=25) as response:
        status_code = response.getcode()
        response_headers = {k: v for k, v in response.headers.items()}
        body = response.read(2048).decode("utf-8", errors="replace")
    return status_code, response_headers, body


def _request_with_retry(
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
    accepted_statuses: set[int] | None = None,
    retries: int = 12,
    delay_seconds: int = 5,
) -> tuple[int, dict[str, str], str]:
    expected_statuses = accepted_statuses or {200}
    last_error: str | None = None

    for attempt in range(1, retries + 1):
        try:
            status_code, response_headers, response_body = _http_request(method, url, headers=headers, body=body)
            if status_code in expected_statuses:
                return status_code, response_headers, response_body
            last_error = f"Unexpected status {status_code}"
        except urllib.error.HTTPError as exc:
            error_body = exc.read(2048).decode("utf-8", errors="replace")
            response_headers = {k: v for k, v in exc.headers.items()}
            if exc.code in expected_statuses:
                return exc.code, response_headers, error_body
            last_error = f"HTTP {exc.code}: {error_body}"
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = str(exc)

        if attempt < retries:
            print(f"Attempt {attempt}/{retries} failed for {method} {url}. Retrying in {delay_seconds}s...")
            time.sleep(delay_seconds)

    raise RuntimeError(f"Request failed after {retries} attempts for {method} {url}: {last_error}")


def _origin_from_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    if not parsed.scheme or not parsed.netloc:
        raise ValueError(f"Invalid URL for origin extraction: {url}")
    return f"{parsed.scheme}://{parsed.netloc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Deployment smoke check for backend and frontend endpoints")
    parser.add_argument("--backend-health-url", required=True, help="Backend health endpoint URL")
    parser.add_argument("--frontend-url", required=True, help="Frontend root URL")
    parser.add_argument(
        "--auth-login-url",
        default="",
        help="Optional auth login URL for negative-login smoke test (expects HTTP 401).",
    )
    parser.add_argument(
        "--auth-test-email",
        default="smoke-check@example.com",
        help="Email sent to auth login endpoint when --auth-login-url is provided.",
    )
    parser.add_argument(
        "--auth-test-password",
        default="invalid-password",
        help="Password sent to auth login endpoint when --auth-login-url is provided.",
    )
    parser.add_argument(
        "--origin",
        default="",
        help="Explicit origin value for CORS check. Defaults to frontend URL origin.",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=12,
        help="Retry attempts for endpoint checks.",
    )
    parser.add_argument(
        "--delay-seconds",
        type=int,
        default=5,
        help="Delay between retry attempts.",
    )
    args = parser.parse_args()

    summary: list[dict[str, str | int]] = []

    try:
        status_code, _, body = _request_with_retry(
            "GET",
            args.frontend_url,
            accepted_statuses={200},
            retries=args.retries,
            delay_seconds=args.delay_seconds,
        )
        if status_code >= 400:
            print(f"Frontend check failed with status {status_code}: {args.frontend_url}")
            return 1
        summary.append({"check": "frontend", "status": status_code, "url": args.frontend_url})

        origin = args.origin or _origin_from_url(args.frontend_url)
        backend_status, backend_headers, backend_body = _request_with_retry(
            "GET",
            args.backend_health_url,
            headers={"Origin": origin},
            accepted_statuses={200},
            retries=args.retries,
            delay_seconds=args.delay_seconds,
        )
        if backend_status >= 400:
            print(f"Backend health check failed with status {backend_status}: {args.backend_health_url}")
            return 1

        allow_origin = backend_headers.get("Access-Control-Allow-Origin", "")
        if allow_origin not in {"*", origin}:
            print(
                "CORS check failed: expected Access-Control-Allow-Origin to match origin or '*'. "
                f"Got '{allow_origin}' for origin '{origin}'."
            )
            return 1

        payload = backend_body.strip()
        if payload:
            try:
                data = json.loads(payload)
                if data.get("status") != "ok":
                    print("Backend health payload does not contain status=ok")
                    return 1
            except json.JSONDecodeError:
                print("Backend health response is not valid JSON")
                return 1

        summary.append({"check": "backend-health", "status": backend_status, "url": args.backend_health_url})
        summary.append({"check": "cors", "status": 200, "url": origin})

        if args.auth_login_url:
            auth_body = json.dumps(
                {
                    "email": args.auth_test_email,
                    "password": args.auth_test_password,
                }
            ).encode("utf-8")

            auth_status, _, _ = _request_with_retry(
                "POST",
                args.auth_login_url,
                headers={"Content-Type": "application/json"},
                body=auth_body,
                accepted_statuses={401},
                retries=args.retries,
                delay_seconds=args.delay_seconds,
            )
            summary.append({"check": "auth-negative-login", "status": auth_status, "url": args.auth_login_url})

    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, RuntimeError) as exc:
        print(f"Smoke check request failed: {exc}")
        return 1
    except ValueError as exc:
        print(str(exc))
        return 1

    print("Smoke checks passed")
    for row in summary:
        print(f"- {row['check']}: {row['status']} ({row['url']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

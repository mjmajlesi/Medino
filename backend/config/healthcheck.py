"""Probe the HTTP API from inside the backend container."""

import os
from urllib.request import Request, urlopen


def main():
    hosts = (part.strip() for part in os.environ.get("ALLOWED_HOSTS", "").split(","))
    host = next((part for part in hosts if part and part != "*" and not part.startswith(".")), "localhost")
    request = Request(
        "http://127.0.0.1:8000/api/health/",
        headers={"Host": host, "X-Forwarded-Proto": "https"},
    )
    with urlopen(request, timeout=3) as response:
        if response.status != 200:
            raise SystemExit(1)


if __name__ == "__main__":
    main()

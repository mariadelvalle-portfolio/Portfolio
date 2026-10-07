"""Generate local secrets, then bootstrap Umami after docker compose starts it."""

import json
import os
from pathlib import Path
import secrets
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
BASE_URL = "http://192.168.1.170:3003"
WEBSITE_ID = "9bff8383-9d93-4e1e-a158-c5a337184bc4"


def write_private(path, content):
    # Exclusive creation: never overwrite credentials for an existing database.
    with os.fdopen(os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600), "w") as f:
        f.write(content)


def request(path, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(
        BASE_URL + path,
        data=json.dumps(data).encode() if data is not None else None,
        headers=headers,
    )
    with urlopen(req, timeout=30) as response:
        return json.load(response)


def prepare():
    env = ROOT / ".env.umami"
    if not env.exists():
        password = secrets.token_hex(32)
        write_private(env, (
            "POSTGRES_USER=umami\nPOSTGRES_DB=umami\n"
            f"POSTGRES_PASSWORD={password}\n"
            f"DATABASE_URL=postgresql://umami:{password}@umami-db:5432/umami\n"
            f"APP_SECRET={secrets.token_hex(32)}\n"
            f"TWO_FACTOR_ENCRYPTION_KEY={secrets.token_hex(32)}\n"
        ))
    admin = ROOT / ".env.umami-admin"
    if not admin.exists():
        write_private(admin, f"UMAMI_ADMIN_PASSWORD={secrets.token_urlsafe(24)}\n")
    print("Local credentials ready (permissions 0600; values not displayed).")


def bootstrap():
    password = (ROOT / ".env.umami-admin").read_text().strip().split("=", 1)[1]
    try:
        auth = request("/api/auth/login", {"username": "admin", "password": password})
    except HTTPError as error:
        if error.code not in (400, 401):
            raise
        auth = request("/api/auth/login", {"username": "admin", "password": "umami"})
        request(f"/api/users/{auth['user']['id']}", {"password": password}, auth["token"])
        auth = request("/api/auth/login", {"username": "admin", "password": password})
    token = auth["token"]
    try:
        website = request(f"/api/websites/{WEBSITE_ID}", token=token)
    except HTTPError as error:
        if error.code not in (403, 404):
            raise
        website = None
    if not website:
        website = request("/api/websites", {
            "id": WEBSITE_ID,
            "name": "María del Valle · Portfolio",
            "domain": "mariadelvalle.work",
        }, token)
    print(f"Umami ready: {BASE_URL}; website ID: {website['id']}")
    print("Admin password stored in .env.umami-admin (not printed).")


if __name__ == "__main__":
    if sys.argv[1:] == ["prepare"]:
        prepare()
    elif sys.argv[1:] == ["bootstrap"]:
        bootstrap()
    else:
        raise SystemExit("Usage: python3 setup-umami.py prepare|bootstrap")

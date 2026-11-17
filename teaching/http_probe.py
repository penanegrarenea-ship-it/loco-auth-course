#!/usr/bin/env python3
"""Live HTTP probe for the generated saas_app.

Reads SAAS_TEST_PASSWORD from the environment and never prints it.
Tokens, API keys, password hashes, and JWTs are used in-process and
replaced with labels before anything is written.
"""

from __future__ import annotations

import base64
import json
import os
import secrets
import sqlite3
import sys
import time
import urllib.error
import urllib.request

BASE = os.environ.get("BASE", "http://127.0.0.1:43123")
DB_PATH = os.environ.get("DB", "saas_app_development.sqlite")
PASSWORD = os.environ.get("SAAS_TEST_PASSWORD") or secrets.token_urlsafe(18)

NEW_PASSWORD = PASSWORD + "-next"
SECRETS: set[str] = {PASSWORD, NEW_PASSWORD}

LINES: list[str] = []


def remember(*values: object) -> None:
    for value in values:
        if isinstance(value, str) and len(value) >= 8:
            SECRETS.add(value)


def redact(text: str) -> str:
    redacted = text
    for secret in sorted(SECRETS, key=len, reverse=True):
        if secret:
            redacted = redacted.replace(secret, "<redacted>")
    return redacted


def record(name: str, status: int, body: str, note: str = "") -> None:
    body = redact(body).replace("\n", "\\n")
    if len(body) > 400:
        body = body[:400] + "…"
    LINES.append(f"{name}\t{status}\t{body}\t{note}")


def request(method: str, path: str, body: dict | None = None, headers: dict | None = None):
    data = None
    hdrs = {"accept": "application/json"}
    if headers:
        hdrs.update(headers)
    if body is not None:
        data = json.dumps(body).encode()
        hdrs["content-type"] = "application/json"
    req = urllib.request.Request(BASE + path, data=data, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read()
            return resp.status, raw.decode("utf-8", "replace"), dict(resp.headers)
    except urllib.error.HTTPError as err:
        raw = err.read()
        return err.code, raw.decode("utf-8", "replace"), dict(err.headers)


def db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con


def user_row(email: str) -> sqlite3.Row | None:
    con = db()
    row = con.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    con.close()
    return row


def set_column(email: str, column: str, value: str | None) -> None:
    if column not in {
        "reset_sent_at",
        "magic_link_expiration",
        "email_verification_sent_at",
    }:
        raise SystemExit("refusing unexpected column")
    con = db()
    con.execute(f"UPDATE users SET {column} = ? WHERE email = ?", (value, email))
    con.commit()
    con.close()


def claim_keys(token: str) -> str:
    remember(token)
    parts = token.split(".")
    if len(parts) != 3:
        return "not-a-compact-jwt"
    def dec(seg: str):
        pad = "=" * (-len(seg) % 4)
        return json.loads(base64.urlsafe_b64decode(seg + pad))

    header = dec(parts[0])
    claims = dec(parts[1])
    exp = claims.get("exp")
    now = int(time.time())
    exp_delta = None if not isinstance(exp, int) else exp - now
    # Report keys and the expiry delta only. Do not report pid or the token.
    return (
        f"header_keys={sorted(header)} alg={header.get('alg')} typ={header.get('typ')} "
        f"claim_keys={sorted(claims)} exp_delta_seconds={exp_delta} "
        f"extra_claim_count={len([k for k in claims if k not in {'pid', 'exp'}])}"
    )


def main() -> None:
    email_unverified = "student-unverified@example.com"
    email = "student-main@example.com"
    unknown = "nobody@example.com"
    bad_domain = "student@example.org"

    for method, path in [
        ("GET", "/_health"),
        ("GET", "/_ping"),
        ("GET", "/_readiness"),
        ("GET", "/"),
        ("GET", "/static/image.png"),
    ]:
        status, body, hdrs = request(method, path)
        if path == "/":
            note = f"content-type={hdrs.get('Content-Type')} contains_hello={'hello-world' in body or 'Hello' in body}"
            record(f"{method} {path}", status, "<html-body-redacted>", note)
        elif path.endswith(".png"):
            record(f"{method} {path}", status, f"bytes={len(body)}", hdrs.get("Content-Type", ""))
        else:
            record(f"{method} {path}", status, body)

    status, body, _ = request(
        "POST",
        "/api/auth/register",
        {"name": "Unverified", "email": email_unverified, "password": PASSWORD},
    )
    record("POST /api/auth/register unverified-user", status, body)
    row = user_row(email_unverified)
    if row is None:
        record("db unverified user", 0, "missing")
    else:
        remember(row["password"], row["api_key"], row["pid"], row["email_verification_token"])
        record(
            "db after register unverified",
            0,
            "row-present",
            "password_prefix_argon2id="
            + str(str(row["password"]).startswith("$argon2id$"))
            + " verified_at_null="
            + str(row["email_verified_at"] is None)
            + " verification_token_present="
            + str(row["email_verification_token"] is not None)
            + " api_key_prefix_lo="
            + str(str(row["api_key"]).startswith("lo-"))
            + " pid_present="
            + str(bool(row["pid"])),
        )

    status, body, _ = request(
        "POST",
        "/api/auth/login",
        {"email": email_unverified, "password": PASSWORD},
    )
    login_unverified = {}
    try:
        login_unverified = json.loads(body)
    except json.JSONDecodeError:
        login_unverified = {}
    if isinstance(login_unverified, dict) and "token" in login_unverified:
        remember(login_unverified["token"], str(login_unverified.get("pid", "")))
    record(
        "POST /api/auth/login before verify",
        status,
        json.dumps(
            {
                "keys": sorted(login_unverified) if isinstance(login_unverified, dict) else [],
                "is_verified": login_unverified.get("is_verified")
                if isinstance(login_unverified, dict)
                else None,
                "name": login_unverified.get("name") if isinstance(login_unverified, dict) else None,
            }
        ),
    )

    status, body, _ = request(
        "POST",
        "/api/auth/register",
        {"name": "Main Student", "email": email, "password": PASSWORD},
    )
    record("POST /api/auth/register main", status, body)
    status, body, _ = request(
        "POST",
        "/api/auth/register",
        {"name": "Main Student", "email": email, "password": PASSWORD},
    )
    record("POST /api/auth/register duplicate", status, body)
    con = db()
    count = con.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,)).fetchone()[0]
    con.close()
    record("db duplicate email count", 0, str(count))

    status, body, _ = request("GET", "/api/auth/verify/not-a-real-token")
    record("GET /api/auth/verify/{invalid}", status, body)
    status, body, _ = request("POST", "/api/auth/verify", {"token": "not-used"})
    record("POST /api/auth/verify (no such route)", status, body)

    row = user_row(email)
    token = row["email_verification_token"]
    remember(token, row["password"], row["api_key"], row["pid"])
    sent_at_before = row["email_verification_sent_at"]
    # Verification lookup does not read sent_at. Move it a day back and still verify.
    set_column(email, "email_verification_sent_at", "2000-01-01T00:00:00+00:00")
    status, body, _ = request("GET", f"/api/auth/verify/{token}")
    record("GET /api/auth/verify/{token} after sent_at backdated", status, body)
    row = user_row(email)
    record(
        "db after verify",
        0,
        "checked",
        f"verified_at_set={row['email_verified_at'] is not None} token_cleared={row['email_verification_token'] is None} sent_at_was={sent_at_before is not None}",
    )
    status, body, _ = request("GET", f"/api/auth/verify/{token}")
    record("GET /api/auth/verify/{token} replay", status, body)

    status, body, _ = request(
        "POST", "/api/auth/login", {"email": email, "password": "wrong-password"}
    )
    record("POST /api/auth/login wrong password", status, body)
    status, body, _ = request(
        "POST", "/api/auth/login", {"email": unknown, "password": PASSWORD}
    )
    record("POST /api/auth/login unknown email", status, body)
    status, body, _ = request(
        "POST", "/api/auth/login", {"email": email, "password": PASSWORD}
    )
    login = json.loads(body)
    remember(login.get("token", ""), str(login.get("pid", "")))
    record(
        "POST /api/auth/login valid",
        status,
        json.dumps(
            {
                "keys": sorted(login),
                "is_verified": login.get("is_verified"),
                "name": login.get("name"),
                "jwt": claim_keys(login["token"]),
            }
        ),
    )
    jwt = login["token"]

    status, body, _ = request("GET", "/api/auth/current")
    record("GET /api/auth/current missing", status, body)
    status, body, _ = request(
        "GET", "/api/auth/current", headers={"authorization": "Bearer not-a-jwt"}
    )
    record("GET /api/auth/current invalid", status, body)
    mutated = jwt[:-4] + ("AAAA" if not jwt.endswith("AAAA") else "BBBB")
    remember(mutated)
    status, body, _ = request(
        "GET", "/api/auth/current", headers={"authorization": f"Bearer {mutated}"}
    )
    record("GET /api/auth/current bad signature", status, body)
    status, body, hdrs = request(
        "GET", "/api/auth/current", headers={"authorization": f"Bearer {jwt}"}
    )
    current = json.loads(body)
    remember(str(current.get("pid", "")), str(current.get("email", "")))
    record(
        "GET /api/auth/current bearer",
        status,
        json.dumps({"keys": sorted(current), "name": current.get("name")}),
    )

    status, body, _ = request("POST", "/api/auth/forgot", {"email": unknown})
    record("POST /api/auth/forgot unknown", status, body)
    status, body, _ = request("POST", "/api/auth/forgot", {"email": email})
    record("POST /api/auth/forgot known", status, body)
    row = user_row(email)
    reset_token = row["reset_token"]
    remember(reset_token)
    record(
        "db after forgot",
        0,
        "checked",
        f"reset_token_present={reset_token is not None} reset_sent_at_present={row['reset_sent_at'] is not None}",
    )
    status, body, _ = request(
        "POST",
        "/api/auth/reset",
        {"token": "not-a-real-reset-token", "password": NEW_PASSWORD},
    )
    record("POST /api/auth/reset unknown token", status, body)
    status, body, _ = request(
        "POST", "/api/auth/login", {"email": email, "password": PASSWORD}
    )
    record("POST /api/auth/login still old password after bad reset", status, body if status != 200 else "login-ok-body-redacted")

    # Expire the reset token by rewriting sent_at, then confirm the password did not change.
    set_column(email, "reset_sent_at", "2000-01-01T00:00:00+00:00")
    status, body, _ = request(
        "POST",
        "/api/auth/reset",
        {"token": reset_token, "password": NEW_PASSWORD},
    )
    record("POST /api/auth/reset expired token", status, body)
    status, body, _ = request(
        "POST", "/api/auth/login", {"email": email, "password": NEW_PASSWORD}
    )
    record("POST /api/auth/login new password after expired reset", status, body if status != 200 else "login-ok-body-redacted")
    status, body, _ = request(
        "POST", "/api/auth/login", {"email": email, "password": PASSWORD}
    )
    record("POST /api/auth/login old password after expired reset", status, body if status != 200 else "login-ok-body-redacted")

    status, body, _ = request("POST", "/api/auth/forgot", {"email": email})
    row = user_row(email)
    reset_token = row["reset_token"]
    remember(reset_token)
    status, body, _ = request(
        "POST",
        "/api/auth/reset",
        {"token": reset_token, "password": NEW_PASSWORD},
    )
    record("POST /api/auth/reset valid", status, body)
    row = user_row(email)
    record(
        "db after valid reset",
        0,
        "checked",
        f"reset_token_cleared={row['reset_token'] is None} reset_sent_at_cleared={row['reset_sent_at'] is None} password_prefix_argon2id={str(row['password']).startswith('$argon2id$')}",
    )
    status, body, _ = request(
        "POST", "/api/auth/login", {"email": email, "password": PASSWORD}
    )
    record("POST /api/auth/login old password after reset", status, body)
    status, body, _ = request(
        "POST", "/api/auth/login", {"email": email, "password": NEW_PASSWORD}
    )
    record(
        "POST /api/auth/login new password after reset",
        status,
        "login-ok-body-redacted" if status == 200 else body,
    )
    status, body, _ = request(
        "GET", "/api/auth/current", headers={"authorization": f"Bearer {jwt}"}
    )
    record("GET /api/auth/current old jwt after password reset", status, "body-redacted" if status == 200 else body)

    status, body, _ = request(
        "POST", "/api/auth/resend-verification-mail", {"email": email}
    )
    record("POST /api/auth/resend already verified", status, body)
    row = user_row(email)
    record(
        "db resend verified",
        0,
        "checked",
        f"verification_token_still_null={row['email_verification_token'] is None}",
    )
    before = user_row(email_unverified)["email_verification_token"]
    remember(before)
    status, body, _ = request(
        "POST", "/api/auth/resend-verification-mail", {"email": email_unverified}
    )
    record("POST /api/auth/resend unverified", status, body)
    after = user_row(email_unverified)["email_verification_token"]
    remember(after)
    record(
        "db resend unverified",
        0,
        "checked",
        f"token_present={after is not None} token_rotated={before != after}",
    )
    status, body, _ = request(
        "POST", "/api/auth/resend-verification-mail", {"email": unknown}
    )
    record("POST /api/auth/resend unknown", status, body)

    status, body, _ = request("POST", "/api/auth/magic-link", {"email": bad_domain})
    record("POST /api/auth/magic-link disallowed domain", status, body)
    status, body, _ = request("POST", "/api/auth/magic-link", {"email": unknown})
    record("POST /api/auth/magic-link unknown allowed domain", status, body)
    status, body, _ = request("POST", "/api/auth/magic-link", {"email": email})
    record("POST /api/auth/magic-link known", status, body)
    row = user_row(email)
    magic = row["magic_link_token"]
    remember(magic)
    record(
        "db magic issued",
        0,
        "checked",
        f"token_len={len(magic) if magic else 0} expiration_present={row['magic_link_expiration'] is not None}",
    )
    status, body, _ = request("GET", "/api/auth/magic-link/not-a-real-magic-token")
    record("GET /api/auth/magic-link/{invalid}", status, body)
    status, body, _ = request("GET", f"/api/auth/magic-link/{magic}")
    magic_login = {}
    try:
        magic_login = json.loads(body)
    except json.JSONDecodeError:
        magic_login = {}
    if isinstance(magic_login, dict):
        remember(magic_login.get("token", ""), str(magic_login.get("pid", "")))
    record(
        "GET /api/auth/magic-link/{token}",
        status,
        json.dumps(
            {
                "keys": sorted(magic_login) if isinstance(magic_login, dict) else [],
                "is_verified": magic_login.get("is_verified")
                if isinstance(magic_login, dict)
                else None,
            }
        ),
    )
    row = user_row(email)
    record(
        "db magic consumed",
        0,
        "checked",
        f"token_cleared={row['magic_link_token'] is None} expiration_cleared={row['magic_link_expiration'] is None}",
    )
    status, body, _ = request("GET", f"/api/auth/magic-link/{magic}")
    record("GET /api/auth/magic-link/{token} replay", status, body)

    status, body, _ = request("POST", "/api/auth/magic-link", {"email": email})
    magic = user_row(email)["magic_link_token"]
    remember(magic)
    set_column(email, "magic_link_expiration", "2000-01-01T00:00:00+00:00")
    status, body, _ = request("GET", f"/api/auth/magic-link/{magic}")
    record("GET /api/auth/magic-link/{token} expired", status, body)
    row = user_row(email)
    record(
        "db magic expired not cleared",
        0,
        "checked",
        f"token_still_present={row['magic_link_token'] is not None}",
    )

    # Shape only: no disabled/role columns exist.
    cols = [r["name"] for r in db().execute("PRAGMA table_info(users)")]
    record(
        "users columns",
        0,
        ",".join(cols),
        "has_disabled="
        + str(any("disab" in c or c == "role" or "refresh" in c for c in cols)),
    )

    sys.stdout.write("\n".join(LINES) + "\n")


if __name__ == "__main__":
    main()

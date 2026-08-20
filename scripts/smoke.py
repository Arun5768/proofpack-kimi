"""Run a disposable end-to-end check against a deployed ProofPack Worker."""

from __future__ import annotations

import http.cookiejar
import json
import secrets
import sys
import urllib.request
import urllib.error


BASE_URL = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8787").rstrip("/")
cookies = http.cookiejar.CookieJar()
client = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies))
username = f"release_{secrets.token_hex(4)}"
password = f"{secrets.token_urlsafe(20)}!Aa1"
registered = False


def request(path: str, method: str = "GET", body: dict | None = None) -> dict:
    payload = json.dumps(body).encode() if body is not None else None
    headers = {
        "User-Agent": "Mozilla/5.0 ProofPack Release Check",
        "Accept": "application/json",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
        headers["Origin"] = BASE_URL
    try:
        response = client.open(
            urllib.request.Request(f"{BASE_URL}{path}", data=payload, headers=headers, method=method),
            timeout=45,
        )
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")
        raise RuntimeError(f"{method} {path} failed ({error.code}): {detail}") from error
    return json.loads(response.read().decode())


try:
    health = request("/api/health")
    account = request("/api/auth/register", "POST", {"username": username, "password": password})
    registered = bool(account.get("user"))
    workspace = request(
        "/api/workspaces",
        "POST",
        {
            "name": "Release check",
            "target": "Kimi Ambassador Program",
            "description": "Testing the complete evidence-to-answer flow before public launch.",
        },
    )
    workspace_id = workspace["workspace"]["id"]
    request(
        f"/api/workspaces/{workspace_id}/evidence",
        "POST",
        {
            "type": "project",
            "title": "ProofPack production build",
            "details": "Designed and deployed a complete Cloudflare application with accounts, saved workspaces, source checks, answer history, and account recovery.",
            "metric": "Production deployment completed",
        },
    )
    request(
        f"/api/workspaces/{workspace_id}/evidence",
        "POST",
        {
            "type": "event",
            "title": "GitHub Copilot Dev Days",
            "details": "Helped organize a practical GitHub Copilot Dev Days workshop for developers and students, including hands-on activities and participant support.",
            "metric": "97 attendees",
        },
    )
    generated = request(
        f"/api/workspaces/{workspace_id}/generate",
        "POST",
        {
            "question": "Why would you be a useful Kimi Ambassador?",
            "tone": "clear",
            "maxChars": "600",
        },
    )["generation"]
    answer_length = len(generated["answer"])
    print(
        json.dumps(
            {
                "health": health.get("ok"),
                "configured": health.get("kimiConfigured"),
                "model": health.get("model"),
                "answerLength": answer_length,
                "factsUsed": len(generated.get("factsUsed", [])),
                "warnings": len(generated.get("warnings", [])),
                "withinLimit": answer_length <= 600,
            },
            indent=2,
        )
    )
finally:
    if registered:
        try:
            request("/api/account", "DELETE", {"password": password})
        except Exception:
            pass

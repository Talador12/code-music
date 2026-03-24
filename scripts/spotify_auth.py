#!/usr/bin/env python3
"""Spotify OAuth2 authentication — gets a token and saves it locally.

SETUP (one-time, ~3 minutes):
  1. Go to https://developer.spotify.com/dashboard
  2. Click "Create app"
     - App name: code-music (or anything)
     - Redirect URI: http://localhost:8888/callback
     - Check "Web API"
  3. Copy your Client ID and Client Secret
  4. Run this script:

     python scripts/spotify_auth.py --client-id YOUR_ID --client-secret YOUR_SECRET

  Or set env vars:
     export SPOTIFY_CLIENT_ID=your_id
     export SPOTIFY_CLIENT_SECRET=your_secret
     python scripts/spotify_auth.py

The token is saved to .spotify_token (gitignored).
Run spotify_taste.py after this to profile your music taste.
"""

from __future__ import annotations

import argparse
import base64
import http.server
import json
import os
import secrets
import sys
import threading
import time
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

TOKEN_FILE = Path(__file__).parent.parent / ".spotify_token"
REDIRECT_URI = "http://localhost:8888/callback"

# Scopes needed to read your listening history and playlists
SCOPES = " ".join(
    [
        "user-top-read",  # top artists and tracks
        "user-read-recently-played",  # recent listening
        "playlist-read-private",  # private playlists
        "playlist-read-collaborative",
        "user-library-read",  # saved songs
        "user-follow-read",  # followed artists
    ]
)


class _CallbackHandler(http.server.BaseHTTPRequestHandler):
    """Minimal HTTP handler that captures the OAuth callback."""

    code: str | None = None
    state: str | None = None

    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        _CallbackHandler.code = params.get("code", [None])[0]
        _CallbackHandler.state = params.get("state", [None])[0]
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(b"""
        <html><body style="font-family:sans-serif;padding:40px">
        <h2>&#10003; Authorized</h2>
        <p>code-music has access to your Spotify data.</p>
        <p>You can close this tab and return to the terminal.</p>
        </body></html>""")

    def log_message(self, *args):
        pass  # suppress request logs


def _exchange_code(code: str, client_id: str, client_secret: str) -> dict:
    """Exchange auth code for access + refresh tokens."""
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode(
        {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
        }
    ).encode()
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _refresh_token(refresh: str, client_id: str, client_secret: str) -> dict:
    """Get a fresh access token from a stored refresh token."""
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    data = urllib.parse.urlencode(
        {
            "grant_type": "refresh_token",
            "refresh_token": refresh,
        }
    ).encode()
    req = urllib.request.Request(
        "https://accounts.spotify.com/api/token",
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def load_token(client_id: str, client_secret: str) -> str | None:
    """Load a saved token, refreshing it if expired."""
    if not TOKEN_FILE.exists():
        return None
    data = json.loads(TOKEN_FILE.read_text())
    if data.get("client_id") != client_id:
        return None  # different app, re-auth needed
    # Check expiry (with 60s buffer)
    if time.time() < data.get("expires_at", 0) - 60:
        return data["access_token"]
    # Refresh
    try:
        refreshed = _refresh_token(data["refresh_token"], client_id, client_secret)
        data["access_token"] = refreshed["access_token"]
        data["expires_at"] = time.time() + refreshed.get("expires_in", 3600)
        if "refresh_token" in refreshed:
            data["refresh_token"] = refreshed["refresh_token"]
        TOKEN_FILE.write_text(json.dumps(data, indent=2))
        return data["access_token"]
    except Exception as e:
        print(f"Token refresh failed: {e}")
        return None


def authorize(client_id: str, client_secret: str) -> str:
    """Full OAuth2 PKCE flow — opens browser, waits for callback, returns token."""
    state = secrets.token_urlsafe(16)

    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": REDIRECT_URI,
            "scope": SCOPES,
            "state": state,
        }
    )

    # Start local callback server
    server = http.server.HTTPServer(("localhost", 8888), _CallbackHandler)
    thread = threading.Thread(target=server.handle_request, daemon=True)
    thread.start()

    print("\nOpening Spotify authorization in your browser...")
    print(f"If it doesn't open: {auth_url}\n")
    webbrowser.open(auth_url)

    # Wait for callback (up to 120s)
    timeout = time.time() + 120
    while _CallbackHandler.code is None and time.time() < timeout:
        time.sleep(0.1)

    if _CallbackHandler.code is None:
        print("Timed out waiting for authorization.")
        sys.exit(1)

    if _CallbackHandler.state != state:
        print("State mismatch — possible CSRF. Aborting.")
        sys.exit(1)

    print("Authorization received. Exchanging for token...")
    token_data = _exchange_code(_CallbackHandler.code, client_id, client_secret)

    # Save token
    saved = {
        "client_id": client_id,
        "access_token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token", ""),
        "expires_at": time.time() + token_data.get("expires_in", 3600),
        "scope": token_data.get("scope", ""),
    }
    TOKEN_FILE.write_text(json.dumps(saved, indent=2))
    TOKEN_FILE.chmod(0o600)  # readable only by owner
    print(f"Token saved to {TOKEN_FILE}")
    return token_data["access_token"]


def get_token(client_id: str, client_secret: str) -> str:
    """Get a valid token — from cache or fresh OAuth flow."""
    token = load_token(client_id, client_secret)
    if token:
        print("Using cached token.")
        return token
    return authorize(client_id, client_secret)


def main():
    parser = argparse.ArgumentParser(
        description="Authorize code-music to read your Spotify data",
        epilog="""
Setup: https://developer.spotify.com/dashboard → Create app
       Redirect URI must be: http://localhost:8888/callback
""",
    )
    parser.add_argument("--client-id", default=os.environ.get("SPOTIFY_CLIENT_ID"))
    parser.add_argument("--client-secret", default=os.environ.get("SPOTIFY_CLIENT_SECRET"))
    args = parser.parse_args()

    if not args.client_id or not args.client_secret:
        print("""
ERROR: Need Spotify client credentials.

  1. Go to https://developer.spotify.com/dashboard
  2. Create app  (Redirect URI: http://localhost:8888/callback)
  3. Run:

     export SPOTIFY_CLIENT_ID=your_client_id
     export SPOTIFY_CLIENT_SECRET=your_client_secret
     python scripts/spotify_auth.py
""")
        sys.exit(1)

    token = get_token(args.client_id, args.client_secret)
    print(f"\nSuccess! Token starts with: {token[:20]}...")
    print("Run: python scripts/spotify_taste.py  to profile your music taste")


if __name__ == "__main__":
    main()

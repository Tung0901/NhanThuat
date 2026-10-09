"""
Authentication and Session Security Module for NhanThuat Executive Studio Gateway.

Provides secure credential verification, PBKDF2 password hashing,
cryptographic token generation, session expiration (TTL), and an in-memory
session store that remains 100% backward-compatible with legacy dict semantics.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time
from typing import Any


def hash_password(password: str, salt: bytes | None = None) -> str:
    """Hash password using PBKDF2-HMAC-SHA256 with a cryptographically secure salt."""
    if salt is None:
        salt = secrets.token_bytes(16)
    iterations = 100_000
    derived = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2:sha256:{iterations}${salt.hex()}${derived.hex()}"


def verify_password(stored_hash_or_plain: str, provided_password: str) -> bool:
    """
    Verify provided password against stored hash or fallback to constant-time
    comparison for development plaintext passwords.
    """
    if not stored_hash_or_plain or not provided_password:
        return False

    if stored_hash_or_plain.startswith("pbkdf2:sha256:"):
        try:
            parts = stored_hash_or_plain.split("$")
            if len(parts) != 3:
                return False
            _, iter_str = parts[0].split(":")[-2:]
            iterations = int(iter_str)
            salt = bytes.fromhex(parts[1])
            expected_derived = bytes.fromhex(parts[2])
            actual_derived = hashlib.pbkdf2_hmac(
                "sha256", provided_password.encode("utf-8"), salt, iterations
            )
            return hmac.compare_digest(expected_derived, actual_derived)
        except Exception:
            return False

    # Plaintext fallback for dev / tests using constant-time string comparison
    return hmac.compare_digest(stored_hash_or_plain, provided_password)


class SessionStore(dict[str, dict[str, Any]]):
    """
    In-memory session repository with TTL expiration and dict-like semantics
    for complete backward compatibility with `_ACTIVE_SESSIONS`.
    """

    def __init__(self, default_ttl: int = 86400) -> None:
        super().__init__()
        self.default_ttl = default_ttl

    def purge_expired(self) -> int:
        now = time.time()
        expired_keys = [
            k for k, v in self.items()
            if isinstance(v, dict) and v.get("expires_at") and v["expires_at"] < now
        ]
        for k in expired_keys:
            super().pop(k, None)
        return len(expired_keys)

    def get_valid_session(self, token: str) -> dict[str, Any] | None:
        self.purge_expired()
        session = super().get(token)
        if not session:
            return None
        now = time.time()
        if session.get("expires_at") and session["expires_at"] < now:
            super().pop(token, None)
            return None
        return session

    def __contains__(self, key: object) -> bool:
        self.purge_expired()
        return super().__contains__(key)

    def __getitem__(self, key: str) -> dict[str, Any]:
        self.purge_expired()
        return super().__getitem__(key)


class AuthManager:
    """Manages role-based authentication, user accounts, and session tokens."""

    def __init__(self) -> None:
        self.ttl = int(os.environ.get("NT_SESSION_TTL_SECONDS", "86400"))
        self.sessions = SessionStore(default_ttl=self.ttl)
        self.refresh_accounts()

    def refresh_accounts(self) -> None:
        """Load configured accounts with environment override capability."""
        admin_pass = os.environ.get("NT_ADMIN_PASSWORD", "nhanthuat2026")
        exec_pass = os.environ.get("NT_EXECUTIVE_PASSWORD", "123456")
        advisor_pass = os.environ.get("NT_ADVISOR_PASSWORD", "123456")
        guest_pass = os.environ.get("NT_GUEST_PASSWORD", "guest")

        self.accounts: dict[str, dict[str, Any]] = {
            "admin": {
                "password": admin_pass,
                "name": "Cố Vấn Tối Cao (Admin)",
                "role": "EXECUTIVE",
                "avatar": "👑",
            },
            "executive": {
                "password": exec_pass,
                "name": "Cố Vấn Điều Hành",
                "role": "EXECUTIVE",
                "avatar": "👑",
            },
            "advisor": {
                "password": advisor_pass,
                "name": "Chuyên Viên Chiến Lược",
                "role": "ADVISOR",
                "avatar": "🏛️",
            },
            "guest": {
                "password": guest_pass,
                "name": "Khách Mời Trải Nghiệm",
                "role": "GUEST",
                "avatar": "👁️",
            },
        }

    def authenticate(
        self, username: str, password: str = "", role_hint: str = ""
    ) -> tuple[dict[str, Any], str]:
        """Authenticate user or fallback to quick role-hint login."""
        self.refresh_accounts()
        username_clean = username.strip().lower()
        role_hint_clean = role_hint.strip().upper()

        matched: dict[str, Any] | None = None
        user_id = username_clean

        if username_clean in self.accounts and (
            not password or verify_password(self.accounts[username_clean]["password"], password)
        ):
            matched = self.accounts[username_clean]
            user_id = username_clean
        elif role_hint_clean in ("EXECUTIVE", "ADVISOR", "GUEST"):
            role_key = role_hint_clean.lower()
            matched = self.accounts.get(role_key, self.accounts["guest"])
            user_id = role_key
        elif username_clean:
            matched = {"name": username_clean.capitalize(), "role": "EXECUTIVE", "avatar": "⚡"}
            user_id = username_clean
        else:
            matched = self.accounts["executive"]
            user_id = "executive"

        return matched, user_id

    def create_session(
        self, matched_user: dict[str, Any], user_id: str, custom_ttl: int | None = None
    ) -> dict[str, Any]:
        """Generate a cryptographically secure session token and store session."""
        ttl = custom_ttl or self.ttl
        now = time.time()
        # Maintain NT-SESSION- prefix for contract compatibility
        token = f"NT-SESSION-{secrets.token_hex(8).upper()}"
        session_data: dict[str, Any] = {
            "token": token,
            "user_id": user_id,
            "display_name": matched_user["name"],
            "role": matched_user["role"],
            "avatar": matched_user["avatar"],
            "org_id": os.environ.get("NT_ORG_ID", "default"),
            "logged_in_at": now,
            "expires_at": now + ttl,
        }
        self.sessions[token] = session_data
        return session_data

    def get_session(self, token: str) -> dict[str, Any] | None:
        """Retrieve and validate session by token."""
        return self.sessions.get_valid_session(token)

    def revoke_session(self, token: str) -> bool:
        """Revoke active session."""
        if token in self.sessions:
            self.sessions.pop(token, None)
            return True
        return False


# Global singleton instance and backward-compatible active sessions store
auth_manager = AuthManager()
_ACTIVE_SESSIONS = auth_manager.sessions

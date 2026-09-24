"""
Unit tests for AuthManager, SessionStore, and PBKDF2 password hashing in backend.app.auth.
"""

import time

from backend.app.auth import AuthManager, SessionStore, hash_password, verify_password


def test_password_hash_and_verify():
    pwd = "SecretPassword123!"
    hashed = hash_password(pwd)
    assert hashed.startswith("pbkdf2:sha256:100000$")
    assert verify_password(hashed, pwd) is True
    assert verify_password(hashed, "WrongPassword") is False
    assert verify_password(hashed, "") is False


def test_plaintext_password_fallback():
    assert verify_password("simple_plain", "simple_plain") is True
    assert verify_password("simple_plain", "incorrect") is False


def test_session_store_ttl_expiration():
    store = SessionStore(default_ttl=1)  # 1 second TTL
    now = time.time()
    store["TOKEN_EXPIRED"] = {
        "token": "TOKEN_EXPIRED",
        "user_id": "test_user",
        "expires_at": now - 10,
    }
    store["TOKEN_VALID"] = {
        "token": "TOKEN_VALID",
        "user_id": "test_user",
        "expires_at": now + 60,
    }

    assert "TOKEN_EXPIRED" not in store
    assert "TOKEN_VALID" in store
    assert store.get_valid_session("TOKEN_EXPIRED") is None
    assert store.get_valid_session("TOKEN_VALID") is not None


def test_auth_manager_authenticate_and_create_session(monkeypatch):
    monkeypatch.setenv("NT_ADMIN_PASSWORD", "CustomAdmin2026")
    mgr = AuthManager()

    # Verify custom admin authentication
    matched, user_id = mgr.authenticate("admin", "CustomAdmin2026")
    assert user_id == "admin"
    assert matched["role"] == "EXECUTIVE"

    # Create session
    session = mgr.create_session(matched, user_id)
    token = session["token"]
    assert token.startswith("NT-SESSION-")
    assert mgr.get_session(token) is not None

    # Revoke session
    assert mgr.revoke_session(token) is True
    assert mgr.get_session(token) is None
    assert mgr.revoke_session("NON_EXISTENT") is False

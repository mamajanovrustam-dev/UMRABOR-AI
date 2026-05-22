"""Базовые auth-тесты на хеширование и JWT."""

from datetime import timedelta
from uuid import uuid4

import pytest
from jose import JWTError

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


def test_hash_and_verify_password() -> None:
    hashed = hash_password("Demo-2026!")
    assert verify_password("Demo-2026!", hashed)
    assert not verify_password("wrong", hashed)


def test_access_token_roundtrip() -> None:
    uid = uuid4()
    token = create_access_token(uid, "umrabor")
    payload = decode_token(token)
    assert payload["sub"] == str(uid)
    assert payload["sub_type"] == "umrabor"
    assert payload["type"] == "access"


def test_refresh_token_payload() -> None:
    uid = uuid4()
    token = create_refresh_token(uid, "client")
    payload = decode_token(token)
    assert payload["type"] == "refresh"
    assert payload["sub_type"] == "client"


def test_decode_invalid_token() -> None:
    with pytest.raises(JWTError):
        decode_token("invalid.token.value")


def test_token_includes_subject_type_for_partner() -> None:
    uid = uuid4()
    token = create_access_token(uid, "partner", extra={"partner_id": str(uuid4())})
    payload = decode_token(token)
    assert payload["sub_type"] == "partner"
    assert "partner_id" in payload

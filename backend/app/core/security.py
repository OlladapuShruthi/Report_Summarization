import base64
import binascii
import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional

from fastapi import Header, HTTPException

from app.core.config import settings


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _decode(value: str) -> bytes:
    if not value or any(char not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for char in value):
        raise ValueError("invalid base64url value")
    decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    # Reject alternate encodings that decode to the same bytes. Otherwise a token
    # can be visibly modified only in unused base64 bits and still verify.
    if _encode(decoded) != value:
        raise ValueError("non-canonical base64url value")
    return decoded


def create_access_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": int(time.time()) + settings.ACCESS_TOKEN_EXPIRE_SECONDS}
    encoded_payload = _encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(
        settings.AUTH_SECRET_KEY.encode("utf-8"),
        encoded_payload.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{encoded_payload}.{_encode(signature)}"


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        if token.count(".") != 1:
            raise ValueError("invalid token format")
        encoded_payload, encoded_signature = token.split(".", 1)
        expected_signature = hmac.new(
            settings.AUTH_SECRET_KEY.encode("utf-8"),
            encoded_payload.encode("ascii"),
            hashlib.sha256,
        ).digest()
        if not hmac.compare_digest(_decode(encoded_signature), expected_signature):
            raise ValueError("invalid signature")
        payload = json.loads(_decode(encoded_payload))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise HTTPException(status_code=401, detail="Invalid or expired access token.")
        if not payload.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid or expired access token.")
        return payload
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError, binascii.Error):
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")


async def get_optional_user_id(authorization: Optional[str] = Header(default=None)) -> Optional[str]:
    if not authorization:
        return None
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(status_code=401, detail="Authorization must use a bearer token.")
    payload = decode_access_token(token)
    from app.services.user_service import UserService

    if not await UserService.get_by_id(payload["sub"]):
        raise HTTPException(status_code=401, detail="Authenticated user no longer exists.")
    return payload["sub"]


async def get_current_user_id(authorization: Optional[str] = Header(default=None)) -> str:
    """Require a valid bearer token for every patient-scoped route."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authentication is required.")
    user_id = await get_optional_user_id(authorization)
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication is required.")
    return user_id

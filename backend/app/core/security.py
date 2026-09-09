import base64
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
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


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
    # Ensure token has correct format
    if "." not in token:
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
    # Split payload and signature
    encoded_payload, encoded_signature = token.split(".", 1)
    expected_signature = hmac.new(
        settings.AUTH_SECRET_KEY.encode("utf-8"),
        encoded_payload.encode("ascii"),
        hashlib.sha256,
    ).digest()
    if not hmac.compare_digest(_decode(encoded_signature), expected_signature):
        raise HTTPException(status_code=401, detail="Invalid or expired access token.")
    try:
        payload = json.loads(_decode(encoded_payload))
        if int(payload.get("exp", 0)) < int(time.time()):
            raise HTTPException(status_code=401, detail="Invalid or expired access token.")
        if not payload.get("sub"):
            raise HTTPException(status_code=401, detail="Invalid or expired access token.")
        return payload
    except (ValueError, KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError):
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

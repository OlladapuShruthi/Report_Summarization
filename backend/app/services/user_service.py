import hashlib
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException

from app.database.mongodb import get_database

# In-memory fallback when MongoDB is unavailable
in_memory_users: Dict[str, Dict[str, Any]] = {}


def _hash_password(password: str) -> str:
    """Simple SHA-256 password hash. Sufficient for project demo."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class UserService:

    @staticmethod
    async def get_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        db = get_database()
        if db is not None:
            try:
                user = await db.users.find_one({"user_id": user_id})
                if user:
                    user["_id"] = str(user["_id"])
                    return user
            except Exception:
                pass
        return in_memory_users.get(user_id)

    @staticmethod
    async def register(full_name: str, email: str, password: str) -> Dict[str, Any]:
        """Register a new user account. Raises 409 if email already exists."""
        email = email.strip().lower()

        # Check duplicate in DB
        db = get_database()
        if db is not None:
            try:
                existing = await db.users.find_one({"email": email})
                if existing:
                    raise HTTPException(status_code=409, detail="An account with this email already exists. Please log in.")
            except HTTPException:
                raise
            except Exception:
                pass

        # Also check in-memory store
        for u in in_memory_users.values():
            if u["email"] == email:
                raise HTTPException(status_code=409, detail="An account with this email already exists. Please log in.")

        now = datetime.utcnow().isoformat()
        user: Dict[str, Any] = {
            "user_id": str(uuid.uuid4()),
            "full_name": full_name.strip(),
            "email": email,
            "password_hash": _hash_password(password),
            "created_at": now,
        }

        if db is not None:
            try:
                await db.users.insert_one(dict(user))
            except Exception:
                in_memory_users[user["user_id"]] = user
        else:
            in_memory_users[user["user_id"]] = user

        # Return safe public object (no password hash)
        return {
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "created_at": user["created_at"],
        }

    @staticmethod
    async def login(email: str, password: str) -> Dict[str, Any]:
        """Validate credentials and return the user. Raises 401 on failure, 404 if not found."""
        email = email.strip().lower()
        password_hash = _hash_password(password)

        db = get_database()
        user = None

        if db is not None:
            try:
                user = await db.users.find_one({"email": email})
                if user:
                    user["_id"] = str(user["_id"])
            except Exception:
                pass

        # Fallback to in-memory
        if user is None:
            for u in in_memory_users.values():
                if u["email"] == email:
                    user = u
                    break

        if user is None:
            raise HTTPException(
                status_code=404,
                detail="No account found with this email. Please sign up first."
            )

        if user.get("password_hash") != password_hash:
            raise HTTPException(status_code=401, detail="Incorrect password. Please try again.")

        return {
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "email": user["email"],
            "created_at": user.get("created_at", ""),
        }

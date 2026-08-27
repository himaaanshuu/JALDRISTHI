"""
Authentication Middleware for JALDRISTHI.
Verifies Supabase JWT tokens and manages user sessions.
"""

import os
import time
import jwt
import requests
from typing import Optional, Dict, Any
from functools import wraps
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hcktzgmanojzqcfzecvk.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET", "")

security = HTTPBearer(auto_error=False)


def get_jwt_secret() -> str:
    """Get JWT secret from Supabase or env."""
    global JWT_SECRET
    if JWT_SECRET:
        return JWT_SECRET
    try:
        resp = requests.get(
            f"{SUPABASE_URL}/auth/v1/settings",
            headers={"apikey": SUPABASE_ANON_KEY},
            timeout=5,
        )
        if resp.status_code == 200:
            data = resp.json()
            JWT_SECRET = data.get("jwt_secret", "")
            return JWT_SECRET
    except Exception:
        pass
    return ""


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify Supabase JWT token."""
    try:
        secret = get_jwt_secret()
        if not secret:
            return None
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={"verify_exp": True},
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """Extract user from JWT token. Returns None if not authenticated."""
    if not credentials:
        return None
    return decode_token(credentials.credentials)


def require_auth(user: Optional[Dict[str, Any]] = Depends(get_current_user)) -> Dict[str, Any]:
    """Require authenticated user. Raises 401 if not authenticated."""
    if not user:
        raise HTTPException(status_code=401, detail="Authentication required")
    return user


def require_admin(user: Dict[str, Any] = Depends(require_auth)) -> Dict[str, Any]:
    """Require admin role. Raises 403 if not admin."""
    if user.get("role") != "admin" and user.get("app_metadata", {}).get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


def get_user_id(user: Dict[str, Any]) -> str:
    """Extract user ID from decoded JWT."""
    return user.get("sub", "")


def get_user_role(user: Dict[str, Any]) -> str:
    """Extract user role from decoded JWT or app_metadata."""
    return user.get("app_metadata", {}).get("role", "user")

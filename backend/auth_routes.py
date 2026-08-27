"""
Auth Endpoints for JALDRISTHI.
Handles user profile CRUD, session verification, and role management.
"""

import os
import requests
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
from auth_middleware import require_auth, require_admin, get_user_id, get_user_role
from supabase_client import supabase_request

router = APIRouter(prefix="/api/auth", tags=["auth"])

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://hcktzgmanojzqcfzecvk.supabase.co")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None


class RoleUpdate(BaseModel):
    role: str


class ProfileResponse(BaseModel):
    id: str
    auth_user_id: str
    full_name: str
    email: str
    phone: str
    avatar_url: str
    role: str
    created_at: str
    updated_at: str


@router.get("/me")
async def get_current_profile(user: Dict[str, Any] = Depends(require_auth)):
    """Get current user's profile."""
    user_id = get_user_id(user)
    result = supabase_request("GET", "/profiles", params={
        "auth_user_id": f"eq.{user_id}",
        "select": "*",
    })
    if not result or len(result) == 0:
        raise HTTPException(status_code=404, detail="Profile not found")
    return result[0]


@router.put("/me")
async def update_profile(
    update: ProfileUpdate,
    user: Dict[str, Any] = Depends(require_auth),
):
    """Update current user's profile."""
    user_id = get_user_id(user)
    existing = supabase_request("GET", "/profiles", params={
        "auth_user_id": f"eq.{user_id}",
        "select": "id",
    })
    if not existing or len(existing) == 0:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile_id = existing[0]["id"]
    update_data = {"updated_at": "now()"}
    if update.full_name is not None:
        update_data["full_name"] = update.full_name
    if update.phone is not None:
        update_data["phone"] = update.phone

    result = supabase_request("PATCH", f"/profiles?id=eq.{profile_id}", json_data=update_data)
    return {"status": "updated", "profile_id": profile_id}


@router.get("/users")
async def list_users(user: Dict[str, Any] = Depends(require_admin)):
    """List all user profiles (admin only)."""
    result = supabase_request("GET", "/profiles", params={
        "select": "id,auth_user_id,full_name,email,phone,role,created_at",
        "order": "created_at.desc",
    })
    return {"users": result or []}


@router.put("/users/{profile_id}/role")
async def update_user_role(
    profile_id: str,
    update: RoleUpdate,
    user: Dict[str, Any] = Depends(require_admin),
):
    """Update a user's role (admin only)."""
    if update.role not in ("user", "admin", "viewer"):
        raise HTTPException(status_code=400, detail="Invalid role")
    result = supabase_request("PATCH", f"/profiles?id=eq.{profile_id}", json_data={
        "role": update.role,
        "updated_at": "now()",
    })
    return {"status": "role_updated", "profile_id": profile_id, "role": update.role}


@router.get("/verify")
async def verify_token(user: Dict[str, Any] = Depends(require_auth)):
    """Verify that the current token is valid."""
    return {
        "valid": True,
        "user_id": get_user_id(user),
        "role": get_user_role(user),
        "email": user.get("email", ""),
        "phone": user.get("phone", ""),
    }

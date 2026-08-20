"""
app/routers/users.py
User endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter(prefix="/users", tags=["User"])

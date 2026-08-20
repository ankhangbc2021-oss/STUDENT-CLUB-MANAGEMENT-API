"""
app/routers/auth.py
Register/Login
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

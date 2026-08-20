"""
app/routers/club.py
Câu lạc bộ/Member endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter(prefix="/clubs", tags=["Club"])

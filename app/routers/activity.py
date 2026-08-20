"""
app/routers/activity.py
Hoạt động câu lạc bộ endpoints
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db

router = APIRouter(prefix="/activities", tags=["ClubActivity"])

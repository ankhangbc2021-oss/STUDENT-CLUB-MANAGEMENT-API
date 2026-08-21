"""app/core/limiter.py"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Nhận diện người gọi API
limiter = Limiter(key_func=get_remote_address)

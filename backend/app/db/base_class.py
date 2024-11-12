# backend/app/db/base_class.py
from .base import Base  # noqa

# Import models here for Alembic
from ..models.models import *  # noqa

# backend/app/schemas/base.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
        }
    )

class TimestampedSchema(BaseSchema):
    """Base schema with timestamp fields."""
    created_at: datetime
    updated_at: Optional[datetime] = None

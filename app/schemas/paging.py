from pydantic import BaseModel, Field

class Paging(BaseModel):
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=10, ge=1, le=1000, description="Maximum number of items to return (1-100)")
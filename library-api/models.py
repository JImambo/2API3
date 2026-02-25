from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import field_validator
import re

class Book(SQLModel, table=True):
    # 'table=True' dit à SQLModel que cette classe correspond à une table dans Postgres
    
    id: Optional[int] = Field(default=None, primary_key=True) # Postgres gérera l'auto-incrément
    title: str = Field(index=True, min_length=3, max_length=200)
    author: str = Field(index=True, min_length=2, max_length=100)
    year: Optional[int] = Field(default=None, ge=1000, le=2100)
    genre: Optional[str] = Field(default=None, max_length=50)
    
    # On garde votre validation ISBN
    isbn: Optional[str] = Field(
        default=None, 
        pattern=r"^(978|979)[- ]?\d{1,5}[- ]?\d{1,7}[- ]?\d{1,7}[- ]?\d{1}$"
    )

    # Configuration pour l'exemple dans Swagger
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Le Petit Prince",
                "author": "Antoine de Saint-Exupéry",
                "year": 1943,
                "genre": "Conte",
                "isbn": "978-2070612758"
            }
        }
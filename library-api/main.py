from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional

app = FastAPI(
    title="Library API",
    description="API REST pour gérer une bibliothèque de livres",
    version="1.0.0"
)

# Modèle Pydantic pour la validation
class Book(BaseModel):
    id: Optional[int] = Field(None, description="ID unique (auto-généré)")
    title: str = Field(..., min_length=3, max_length=200, description="Titre du livre")
    author: str = Field(..., min_length=2, max_length=100, description="Auteur du livre")
    year: Optional[int] = Field(None, ge=1000, le=2100, description="Année de publication")
    genre: Optional[str] = Field(None, max_length=50, description="Genre littéraire")
    isbn: Optional[str] = Field(None, max_length=17, description="Code ISBN-13")
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "1984",
                "author": "George Orwell",
                "year": 1949,
                "genre": "Science-fiction dystopique",
                "isbn": "978-0451524935"
            }
        }

# Base de données simulée (en mémoire)
books_db: List[dict] = []
next_id = 1

# Route racine
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Bienvenue sur l'API Library",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "books": "/books"
        }
    }

# GET /books
@app.get(
    "/books",
    response_model=List[Book],
    tags=["Books"],
    summary="Récupérer tous les livres",
    description="Rétourne la liste complète des livres enrégistrés en mémoire"
)
def get_all_books():
    return books_db

# GET /books/{book_id}
@app.get(
    "/books/{book_id}",
    response_model=Book,
    tags=["Books"],
    summary="Récupérer un livre par son ID"
)
def get_book_by_id(book_id: int):
    for book in books_db:
        if book["id"] == book_id:
            return book
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Le livre avec l'ID {book_id} est introuvable."
    )

# POST /books
@app.post(
    "/books",
    status_code=status.HTTP_201_CREATED,
    response_model=Book,
    tags=["Books"],
    summary="Ajouter un nouveau livre"
)
def create_book(book: Book):
    global next_id
    book.id = next_id
    book_data = book.model_dump()
    books_db.append(book_data)
    next_id += 1
    return book


# PUT /books/{book_id}


# PATCH /books/{book_id}


# DELETE /books/{book_id}
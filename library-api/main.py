from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
import re

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
    isbn: Optional[str] = Field(None, pattern=r"^(978|979)[- ]?\d{1,5}[- ]?\d{1,7}[- ]?\d{1,7}[- ]?\d{1}$", max_length=17, description="Format ISBN-13 valide")
    
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
def get_all_books(
    search: Optional[str] = None,
    author: Optional[str] = None, 
    year: Optional[int] = None,
    sort: Optional[str] = "id",
    order: str = "asc",
    page: int = 1,
    limit: int = 10
):
    results = books_db
    
    if search:
        results = [
            b for b in results if search.lower() in b["title"].lower()
        ]
    
    if author:
        results = [b for b in results if author.lower() in b["author"].lower()]
    
    if year:
        results = [b for b in results if b["year"] == year]
    
    reverse_order = True if order.lower() == "desc" else False
    
    try:
        results = sorted(results, key=lambda b: b.get(sort, 0), reverse=reverse_order)
    except Exception:
        pass
    
    skip = (page - 1) * limit
    paginated_results = results[skip: skip + limit]
    
    return paginated_results

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
def create_book(book: Book, response: Response):
    global next_id
    
    book.id = next_id
    book_data = book.model_dump()
    books_db.append(book_data)
    
    response.headers["Location"] = f"/books/{next_id}"
    
    next_id += 1
    
    return book

# PUT /books/{book_id}
@app.put(
    "/books/{book_id}",
    response_model=Book,
    tags=["Books"],
    summary="Remplacer un livre existant"
)
def update_book(book_id: int, book_update: Book):
    for index, book in enumerate(books_db):
        if book["id"] == book_id:
            book_update.id = book_id
            books_db[index] = book_update.model_dump()
            return book_update
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Impossible de mettre à jour : le livre {book_id} n'existe pas"
    )

# PATCH /books/{book_id}
@app.patch(
    "/books/{book_id}", 
    response_model=Book, 
    tags=["Books"],
    summary="Modifier partiellement un livre"
)
def patch_book(book_id: int, book_update: Book):
    for index, existing_book in enumerate(books_db):
        if existing_book["id"] == book_id:
            update_data = book_update.model_dump(exclude_unset=True)
            existing_book.update(update_data)
            existing_book["id"] = book_id
            books_db[index] = existing_book
            return existing_book
            
    raise HTTPException(
        status_code=404, 
        detail="Livre non trouvé"
    )

# DELETE /books/{book_id}
@app.delete(
    "/books/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Books"],
    summary="Supprimer un livre de la bibliothèque"
)
def delete_book(book_id: int):
    for index, book in enumerate(books_db):
        if book["id"] == book_id:
            books_db.pop(index)
            return None
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Action impossible : aucun livre"
    )
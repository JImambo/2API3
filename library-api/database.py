from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://jonathan:password@localhost:5432/library_db"

# L'engine est le moteur qui gère les connexions à la base
engine = create_engine(DATABASE_URL, echo=True) 

# Fonction pour créer les tables (à lancer au démarrage de l'app)
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dépendance pour FastAPI : ouvre une session par requête et la ferme après
def get_session():
    with Session(engine) as session:
        yield session
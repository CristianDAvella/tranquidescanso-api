from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import DATABASE_URL

# Crear motor de base de datos
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Cambiar a True para ver queries SQL
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True  # Verifica la conexión antes de usar
)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependencia para obtener sesión de BD en cada request"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

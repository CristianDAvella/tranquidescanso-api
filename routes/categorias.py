from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.categoria_schema import (
    CategoriaCreate,
    CategoriaUpdate,
    CategoriaResponse,
    CategoriaListResponse
)

router = APIRouter(prefix="/categorias", tags=["categorias"])

@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    """Crear una nueva categoría de hotel"""
    try:
        query = """
        INSERT INTO CATEGORIA (nombre_categoria)
        VALUES (:nombre_categoria)
        RETURNING id_categoria, fecha_cambio
        """
        result = db.execute(text(query), {"nombre_categoria": categoria.nombre_categoria})
        row = result.fetchone()
        db.commit()
        return {"id_categoria": row[0], "nombre_categoria": categoria.nombre_categoria, "fecha_cambio": row[1]}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear categoría: {str(e)}"
        )

@router.get("/", response_model=List[CategoriaListResponse])
def listar_categorias(db: Session = Depends(get_db)):
    """Listar todas las categorías"""
    try:
        query = "SELECT id_categoria, nombre_categoria, fecha_cambio FROM CATEGORIA ORDER BY nombre_categoria"
        result = db.execute(text(query)).fetchall()
        return [{"id_categoria": row[0], "nombre_categoria": row[1], "fecha_cambio": row[2]} for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar categorías: {str(e)}"
        )

@router.get("/{id_categoria}", response_model=CategoriaResponse)
def obtener_categoria_por_id(id_categoria: int, db: Session = Depends(get_db)):
    """Obtener una categoría por ID"""
    try:
        query = "SELECT id_categoria, nombre_categoria, fecha_cambio FROM CATEGORIA WHERE id_categoria = :id_categoria"
        categoria = db.execute(text(query), {"id_categoria": id_categoria}).fetchone()
        if not categoria:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
        return {"id_categoria": categoria[0], "nombre_categoria": categoria[1], "fecha_cambio": categoria[2]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener categoría: {str(e)}"
        )

@router.put("/{id_categoria}", response_model=CategoriaResponse)
def actualizar_categoria(id_categoria: int, categoria: CategoriaUpdate, db: Session = Depends(get_db)):
    """Actualizar una categoría"""
    try:
        query = "SELECT id_categoria FROM CATEGORIA WHERE id_categoria = :id_categoria"
        if not db.execute(text(query), {"id_categoria": id_categoria}).fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
        
        if categoria.nombre_categoria:
            query_update = "UPDATE CATEGORIA SET nombre_categoria = :nombre_categoria, fecha_cambio = NOW() WHERE id_categoria = :id_categoria"
            db.execute(text(query_update), {"nombre_categoria": categoria.nombre_categoria, "id_categoria": id_categoria})
            db.commit()
        
        return obtener_categoria_por_id(id_categoria, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar categoría: {str(e)}"
        )

@router.delete("/{id_categoria}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(id_categoria: int, db: Session = Depends(get_db)):
    """Eliminar una categoría"""
    try:
        query = "DELETE FROM CATEGORIA WHERE id_categoria = :id_categoria"
        result = db.execute(text(query), {"id_categoria": id_categoria})
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoría no encontrada"
            )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar categoría: {str(e)}"
        )

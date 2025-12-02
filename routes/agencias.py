from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.agencia_schema import (
    AgenciaCreate,
    AgenciaUpdate,
    AgenciaResponse,
    AgenciaListResponse
)

router = APIRouter(prefix="/agencias", tags=["agencias"])

@router.post("/", response_model=AgenciaResponse, status_code=status.HTTP_201_CREATED)
def crear_agencia(agencia: AgenciaCreate, db: Session = Depends(get_db)):
    """Crear una nueva agencia de viajes"""
    try:
        query = """
        INSERT INTO AGENCIA_VIAJES (nombre)
        VALUES (:nombre)
        RETURNING id_agencia
        """
        result = db.execute(text(query), {"nombre": agencia.nombre})
        id_agencia = result.scalar()
        db.commit()
        return obtener_agencia_por_id(id_agencia, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear agencia: {str(e)}"
        )

@router.get("/", response_model=List[AgenciaListResponse])
def listar_agencias(db: Session = Depends(get_db)):
    """Listar todas las agencias de viajes"""
    try:
        query = "SELECT id_agencia, nombre FROM AGENCIA_VIAJES ORDER BY nombre"
        result = db.execute(text(query)).fetchall()
        return [{"id_agencia": row[0], "nombre": row[1]} for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar agencias: {str(e)}"
        )

@router.get("/{id_agencia}", response_model=AgenciaResponse)
def obtener_agencia_por_id(id_agencia: int, db: Session = Depends(get_db)):
    """Obtener una agencia por ID"""
    try:
        query = "SELECT id_agencia, nombre FROM AGENCIA_VIAJES WHERE id_agencia = :id_agencia"
        agencia = db.execute(text(query), {"id_agencia": id_agencia}).fetchone()
        if not agencia:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agencia no encontrada"
            )
        return {"id_agencia": agencia[0], "nombre": agencia[1]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener agencia: {str(e)}"
        )

@router.put("/{id_agencia}", response_model=AgenciaResponse)
def actualizar_agencia(id_agencia: int, agencia: AgenciaUpdate, db: Session = Depends(get_db)):
    """Actualizar una agencia"""
    try:
        query = "SELECT id_agencia FROM AGENCIA_VIAJES WHERE id_agencia = :id_agencia"
        if not db.execute(text(query), {"id_agencia": id_agencia}).fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agencia no encontrada"
            )
        
        if agencia.nombre:
            query_update = "UPDATE AGENCIA_VIAJES SET nombre = :nombre WHERE id_agencia = :id_agencia"
            db.execute(text(query_update), {"nombre": agencia.nombre, "id_agencia": id_agencia})
            db.commit()
        
        return obtener_agencia_por_id(id_agencia, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar agencia: {str(e)}"
        )

@router.delete("/{id_agencia}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_agencia(id_agencia: int, db: Session = Depends(get_db)):
    """Eliminar una agencia"""
    try:
        query = "DELETE FROM AGENCIA_VIAJES WHERE id_agencia = :id_agencia"
        result = db.execute(text(query), {"id_agencia": id_agencia})
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Agencia no encontrada"
            )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar agencia: {str(e)}"
        )

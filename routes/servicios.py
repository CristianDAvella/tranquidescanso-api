from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.servicio_schema import (
    ServicioCreate,
    ServicioUpdate,
    ServicioResponse,
    ServicioListResponse
)

router = APIRouter(prefix="/servicios", tags=["servicios"])

@router.post("/", response_model=ServicioResponse, status_code=status.HTTP_201_CREATED)
def crear_servicio(servicio: ServicioCreate, db: Session = Depends(get_db)):
    """Crear un nuevo servicio adicional"""
    try:
        query = """
        INSERT INTO SERVICIO_ADICIONAL (nombre, costo)
        VALUES (:nombre, :costo)
        RETURNING id_servicio
        """
        result = db.execute(text(query), {"nombre": servicio.nombre, "costo": float(servicio.costo)})
        id_servicio = result.scalar()
        db.commit()
        return obtener_servicio_por_id(id_servicio, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear servicio: {str(e)}"
        )

@router.get("/", response_model=List[ServicioListResponse])
def listar_servicios(db: Session = Depends(get_db)):
    """Listar todos los servicios adicionales"""
    try:
        query = "SELECT id_servicio, nombre, costo FROM SERVICIO_ADICIONAL ORDER BY nombre"
        result = db.execute(text(query)).fetchall()
        return [{"id_servicio": row[0], "nombre": row[1], "costo": row[2]} for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar servicios: {str(e)}"
        )

@router.get("/{id_servicio}", response_model=ServicioResponse)
def obtener_servicio_por_id(id_servicio: int, db: Session = Depends(get_db)):
    """Obtener un servicio por ID"""
    try:
        query = "SELECT id_servicio, nombre, costo FROM SERVICIO_ADICIONAL WHERE id_servicio = :id_servicio"
        servicio = db.execute(text(query), {"id_servicio": id_servicio}).fetchone()
        if not servicio:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )
        return {"id_servicio": servicio[0], "nombre": servicio[1], "costo": servicio[2]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener servicio: {str(e)}"
        )

@router.put("/{id_servicio}", response_model=ServicioResponse)
def actualizar_servicio(id_servicio: int, servicio: ServicioUpdate, db: Session = Depends(get_db)):
    """Actualizar un servicio"""
    try:
        query = "SELECT id_servicio FROM SERVICIO_ADICIONAL WHERE id_servicio = :id_servicio"
        if not db.execute(text(query), {"id_servicio": id_servicio}).fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )
        
        campos = []
        params = {"id_servicio": id_servicio}
        if servicio.nombre:
            campos.append("nombre = :nombre")
            params["nombre"] = servicio.nombre
        if servicio.costo:
            campos.append("costo = :costo")
            params["costo"] = float(servicio.costo)
        
        if campos:
            query_update = f"UPDATE SERVICIO_ADICIONAL SET {', '.join(campos)} WHERE id_servicio = :id_servicio"
            db.execute(text(query_update), params)
            db.commit()
        
        return obtener_servicio_por_id(id_servicio, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar servicio: {str(e)}"
        )

@router.delete("/{id_servicio}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_servicio(id_servicio: int, db: Session = Depends(get_db)):
    """Eliminar un servicio"""
    try:
        query = "DELETE FROM SERVICIO_ADICIONAL WHERE id_servicio = :id_servicio"
        result = db.execute(text(query), {"id_servicio": id_servicio})
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Servicio no encontrado"
            )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar servicio: {str(e)}"
        )

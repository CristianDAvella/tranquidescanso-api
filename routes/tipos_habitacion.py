from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.tipo_habitacion_schema import (
    TipoHabitacionCreate,
    TipoHabitacionUpdate,
    TipoHabitacionResponse,
    TipoHabitacionListResponse
)

router = APIRouter(prefix="/tipos-habitacion", tags=["tipos_habitacion"])

@router.post("/", response_model=TipoHabitacionResponse, status_code=status.HTTP_201_CREATED)
def crear_tipo_habitacion(tipo: TipoHabitacionCreate, db: Session = Depends(get_db)):
    """Crear un nuevo tipo de habitación"""
    try:
        query = """
        INSERT INTO TIPO_HABITACION (descripcion, capacidad, valor)
        VALUES (:descripcion, :capacidad, :valor)
        RETURNING id_tipo
        """
        result = db.execute(text(query), {
            "descripcion": tipo.descripcion,
            "capacidad": tipo.capacidad,
            "valor": float(tipo.valor)
        })
        id_tipo = result.scalar()
        db.commit()
        return obtener_tipo_por_id(id_tipo, db)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear tipo de habitación: {str(e)}"
        )

@router.get("/", response_model=List[TipoHabitacionListResponse])
def listar_tipos_habitacion(db: Session = Depends(get_db)):
    """Listar todos los tipos de habitación"""
    try:
        query = "SELECT id_tipo, descripcion, capacidad, valor FROM TIPO_HABITACION ORDER BY descripcion"
        result = db.execute(text(query)).fetchall()
        return [
            {"id_tipo": row[0], "descripcion": row[1], "capacidad": row[2], "valor": row[3]}
            for row in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar tipos: {str(e)}"
        )

@router.get("/{id_tipo}", response_model=TipoHabitacionResponse)
def obtener_tipo_por_id(id_tipo: int, db: Session = Depends(get_db)):
    """Obtener un tipo de habitación por ID"""
    try:
        query = "SELECT id_tipo, descripcion, capacidad, valor FROM TIPO_HABITACION WHERE id_tipo = :id_tipo"
        tipo = db.execute(text(query), {"id_tipo": id_tipo}).fetchone()
        if not tipo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de habitación no encontrado"
            )
        return {"id_tipo": tipo[0], "descripcion": tipo[1], "capacidad": tipo[2], "valor": tipo[3]}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener tipo: {str(e)}"
        )

@router.put("/{id_tipo}", response_model=TipoHabitacionResponse)
def actualizar_tipo_habitacion(id_tipo: int, tipo: TipoHabitacionUpdate, db: Session = Depends(get_db)):
    """Actualizar un tipo de habitación"""
    try:
        query = "SELECT id_tipo FROM TIPO_HABITACION WHERE id_tipo = :id_tipo"
        if not db.execute(text(query), {"id_tipo": id_tipo}).fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de habitación no encontrado"
            )
        
        campos = []
        params = {"id_tipo": id_tipo}
        if tipo.descripcion:
            campos.append("descripcion = :descripcion")
            params["descripcion"] = tipo.descripcion
        if tipo.capacidad:
            campos.append("capacidad = :capacidad")
            params["capacidad"] = tipo.capacidad
        if tipo.valor:
            campos.append("valor = :valor")
            params["valor"] = float(tipo.valor)
        
        if campos:
            query_update = f"UPDATE TIPO_HABITACION SET {', '.join(campos)} WHERE id_tipo = :id_tipo"
            db.execute(text(query_update), params)
            db.commit()
        
        return obtener_tipo_por_id(id_tipo, db)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar tipo: {str(e)}"
        )

@router.delete("/{id_tipo}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_tipo_habitacion(id_tipo: int, db: Session = Depends(get_db)):
    """Eliminar un tipo de habitación"""
    try:
        query = "DELETE FROM TIPO_HABITACION WHERE id_tipo = :id_tipo"
        result = db.execute(text(query), {"id_tipo": id_tipo})
        db.commit()
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tipo de habitación no encontrado"
            )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar tipo: {str(e)}"
        )

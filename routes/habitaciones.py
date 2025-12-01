from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.habitacion_schema import (
    HabitacionCreate, 
    HabitacionUpdate, 
    HabitacionResponse,
    HabitacionListResponse
)

router = APIRouter(prefix="/habitaciones", tags=["habitaciones"])

@router.post("/", response_model=HabitacionResponse, status_code=status.HTTP_201_CREATED)
def crear_habitacion(habitacion: HabitacionCreate, db: Session = Depends(get_db)):
    """Crear una nueva habitación"""
    try:
        query = """
        INSERT INTO HABITACION (numero_habitacion, id_hotel, id_tipo, ocupado)
        VALUES (:numero_habitacion, :id_hotel, :id_tipo, :ocupado)
        RETURNING id_habitacion
        """
        result = db.execute(text(query), {
            "numero_habitacion": habitacion.numero_habitacion,
            "id_hotel": habitacion.id_hotel,
            "id_tipo": habitacion.id_tipo,
            "ocupado": habitacion.ocupado
        })
        id_habitacion = result.scalar()
        db.commit()
        
        return obtener_habitacion_por_id(id_habitacion, db)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear habitación: {str(e)}"
        )

@router.get("/", response_model=List[HabitacionListResponse])
def listar_habitaciones(db: Session = Depends(get_db)):
    """Listar todas las habitaciones"""
    try:
        query = """
        SELECT h.id_habitacion, h.numero_habitacion, ho.nombre, th.descripcion, h.ocupado
        FROM HABITACION h
        INNER JOIN HOTEL ho ON h.id_hotel = ho.id_hotel
        INNER JOIN TIPO_HABITACION th ON h.id_tipo = th.id_tipo
        ORDER BY ho.nombre, h.numero_habitacion
        """
        result = db.execute(text(query)).fetchall()
        return [
            {
                "id_habitacion": row[0],
                "numero_habitacion": row[1],
                "nombre_hotel": row[2],
                "tipo_habitacion": row[3],
                "ocupado": row[4]
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar habitaciones: {str(e)}"
        )

@router.get("/{id_habitacion}", response_model=HabitacionResponse)
def obtener_habitacion_por_id(id_habitacion: int, db: Session = Depends(get_db)):
    """Obtener una habitación por ID"""
    try:
        query = """
        SELECT id_habitacion, numero_habitacion, id_hotel, id_tipo, ocupado
        FROM HABITACION
        WHERE id_habitacion = :id_habitacion
        """
        habitacion = db.execute(text(query), {"id_habitacion": id_habitacion}).fetchone()
        
        if not habitacion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habitación no encontrada"
            )
        
        return {
            "id_habitacion": habitacion[0],
            "numero_habitacion": habitacion[1],
            "id_hotel": habitacion[2],
            "id_tipo": habitacion[3],
            "ocupado": habitacion[4]
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener habitación: {str(e)}"
        )

@router.put("/{id_habitacion}", response_model=HabitacionResponse)
def actualizar_habitacion(id_habitacion: int, habitacion: HabitacionUpdate, db: Session = Depends(get_db)):
    """Actualizar una habitación"""
    try:
        # Verificar que existe
        query = "SELECT id_habitacion FROM HABITACION WHERE id_habitacion = :id_habitacion"
        if not db.execute(text(query), {"id_habitacion": id_habitacion}).fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habitación no encontrada"
            )
        
        # Actualizar
        campos = []
        params = {"id_habitacion": id_habitacion}
        
        if habitacion.numero_habitacion:
            campos.append("numero_habitacion = :numero_habitacion")
            params["numero_habitacion"] = habitacion.numero_habitacion
        if habitacion.ocupado is not None:
            campos.append("ocupado = :ocupado")
            params["ocupado"] = habitacion.ocupado
        
        if campos:
            query_update = f"UPDATE HABITACION SET {', '.join(campos)} WHERE id_habitacion = :id_habitacion"
            db.execute(text(query_update), params)
            db.commit()
        
        return obtener_habitacion_por_id(id_habitacion, db)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar habitación: {str(e)}"
        )

@router.delete("/{id_habitacion}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_habitacion(id_habitacion: int, db: Session = Depends(get_db)):
    """Eliminar una habitación"""
    try:
        query = "DELETE FROM HABITACION WHERE id_habitacion = :id_habitacion"
        result = db.execute(text(query), {"id_habitacion": id_habitacion})
        db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habitación no encontrada"
            )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar habitación: {str(e)}"
        )

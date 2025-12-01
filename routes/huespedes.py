from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.huesped_schema import (
    HuespedCreate, 
    HuespedUpdate, 
    HuespedResponse, 
    HuespedListResponse
)

router = APIRouter(prefix="/huespedes", tags=["huespedes"])

@router.post("/", response_model=HuespedResponse, status_code=status.HTTP_201_CREATED)
def crear_huesped(huesped: HuespedCreate, db: Session = Depends(get_db)):
    """Crear un nuevo huésped"""
    try:
        # Insertar huésped
        query = """
        INSERT INTO HUESPED (numero_id, tipo_id, nombre, direccion)
        VALUES (:numero_id, :tipo_id, :nombre, :direccion)
        """
        db.execute(text(query), {
            "numero_id": huesped.numero_id,
            "tipo_id": huesped.tipo_id,
            "nombre": huesped.nombre,
            "direccion": huesped.direccion
        })
        
        # Insertar teléfonos
        for telefono in huesped.telefonos:
            query_tel = """
            INSERT INTO TELEFONOS_HUESPED (numero_id, telefono)
            VALUES (:numero_id, :telefono)
            """
            db.execute(text(query_tel), {
                "numero_id": huesped.numero_id,
                "telefono": telefono
            })
        
        db.commit()
        
        # Obtener el huésped creado
        return obtener_huesped_por_id(huesped.numero_id, db)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear huésped: {str(e)}"
        )

@router.get("/", response_model=List[HuespedListResponse])
def listar_huespedes(db: Session = Depends(get_db)):
    """Listar todos los huéspedes"""
    try:
        query = "SELECT numero_id, nombre, tipo_id FROM HUESPED"
        result = db.execute(text(query)).fetchall()
        return [{"numero_id": row[0], "nombre": row[1], "tipo_id": row[2]} for row in result]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar huéspedes: {str(e)}"
        )

@router.get("/{numero_id}", response_model=HuespedResponse)
def obtener_huesped_por_id(numero_id: str, db: Session = Depends(get_db)):
    """Obtener un huésped por su número de identificación"""
    try:
        # Obtener datos del huésped
        query = """
        SELECT numero_id, tipo_id, nombre, direccion 
        FROM HUESPED 
        WHERE numero_id = :numero_id
        """
        huesped = db.execute(text(query), {"numero_id": numero_id}).fetchone()
        
        if not huesped:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Huésped no encontrado"
            )
        
        # Obtener teléfonos
        query_tel = "SELECT telefono FROM TELEFONOS_HUESPED WHERE numero_id = :numero_id"
        telefonos = db.execute(text(query_tel), {"numero_id": numero_id}).fetchall()
        telefonos_list = [tel[0] for tel in telefonos]
        
        return {
            "numero_id": huesped[0],
            "tipo_id": huesped[1],
            "nombre": huesped[2],
            "direccion": huesped[3],
            "telefonos": telefonos_list
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener huésped: {str(e)}"
        )

@router.put("/{numero_id}", response_model=HuespedResponse)
def actualizar_huesped(numero_id: str, huesped: HuespedUpdate, db: Session = Depends(get_db)):
    """Actualizar un huésped"""
    try:
        # Verificar que existe
        query = "SELECT numero_id FROM HUESPED WHERE numero_id = :numero_id"
        if not db.execute(text(query), {"numero_id": numero_id}).fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Huésped no encontrado"
            )
        
        # Actualizar
        campos = []
        params = {"numero_id": numero_id}
        
        if huesped.nombre:
            campos.append("nombre = :nombre")
            params["nombre"] = huesped.nombre
        if huesped.direccion:
            campos.append("direccion = :direccion")
            params["direccion"] = huesped.direccion
        
        if campos:
            query_update = f"UPDATE HUESPED SET {', '.join(campos)} WHERE numero_id = :numero_id"
            db.execute(text(query_update), params)
            db.commit()
        
        return obtener_huesped_por_id(numero_id, db)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar huésped: {str(e)}"
        )

@router.delete("/{numero_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_huesped(numero_id: str, db: Session = Depends(get_db)):
    """Eliminar un huésped"""
    try:
        query = "DELETE FROM HUESPED WHERE numero_id = :numero_id"
        result = db.execute(text(query), {"numero_id": numero_id})
        db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Huésped no encontrado"
            )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar huésped: {str(e)}"
        )

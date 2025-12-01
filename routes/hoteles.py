from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.hotel_schema import (
    HotelCreate, 
    HotelUpdate, 
    HotelResponse, 
    HotelListResponse
)

router = APIRouter(prefix="/hoteles", tags=["hoteles"])

@router.post("/", response_model=HotelResponse, status_code=status.HTTP_201_CREATED)
def crear_hotel(hotel: HotelCreate, db: Session = Depends(get_db)):
    """Crear un nuevo hotel"""
    try:
        # Insertar hotel
        query = """
        INSERT INTO HOTEL (nombre, direccion, anio_inauguracion, id_categoria)
        VALUES (:nombre, :direccion, :anio_inauguracion, :id_categoria)
        RETURNING id_hotel
        """
        result = db.execute(text(query), {
            "nombre": hotel.nombre,
            "direccion": hotel.direccion,
            "anio_inauguracion": hotel.anio_inauguracion,
            "id_categoria": hotel.id_categoria
        })
        id_hotel = result.scalar()
        
        # Insertar teléfonos
        for telefono in hotel.telefonos:
            query_tel = """
            INSERT INTO TELEFONOS_HOTEL (id_hotel, telefono)
            VALUES (:id_hotel, :telefono)
            """
            db.execute(text(query_tel), {
                "id_hotel": id_hotel,
                "telefono": telefono
            })
        
        db.commit()
        return obtener_hotel_por_id(id_hotel, db)
    
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear hotel: {str(e)}"
        )

@router.get("/", response_model=List[HotelListResponse])
def listar_hoteles(db: Session = Depends(get_db)):
    """Listar todos los hoteles"""
    try:
        query = """
        SELECT id_hotel, nombre, direccion, anio_inauguracion
        FROM HOTEL
        ORDER BY nombre
        """
        result = db.execute(text(query)).fetchall()
        return [
            {
                "id_hotel": row[0],
                "nombre": row[1],
                "direccion": row[2],
                "anio_inauguracion": row[3]
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar hoteles: {str(e)}"
        )

@router.get("/{id_hotel}", response_model=HotelResponse)
def obtener_hotel_por_id(id_hotel: int, db: Session = Depends(get_db)):
    """Obtener un hotel por ID"""
    try:
        query = """
        SELECT id_hotel, nombre, direccion, anio_inauguracion, id_categoria
        FROM HOTEL
        WHERE id_hotel = :id_hotel
        """
        hotel = db.execute(text(query), {"id_hotel": id_hotel}).fetchone()
        
        if not hotel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel no encontrado"
            )
        
        # Obtener teléfonos
        query_tel = "SELECT telefono FROM TELEFONOS_HOTEL WHERE id_hotel = :id_hotel"
        telefonos = db.execute(text(query_tel), {"id_hotel": id_hotel}).fetchall()
        telefonos_list = [tel[0] for tel in telefonos]
        
        return {
            "id_hotel": hotel[0],
            "nombre": hotel[1],
            "direccion": hotel[2],
            "anio_inauguracion": hotel[3],
            "id_categoria": hotel[4],
            "telefonos": telefonos_list
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener hotel: {str(e)}"
        )

@router.put("/{id_hotel}", response_model=HotelResponse)
def actualizar_hotel(id_hotel: int, hotel: HotelUpdate, db: Session = Depends(get_db)):
    """Actualizar un hotel"""
    try:
        # Verificar que existe
        query = "SELECT id_hotel FROM HOTEL WHERE id_hotel = :id_hotel"
        if not db.execute(text(query), {"id_hotel": id_hotel}).fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel no encontrado"
            )
        
        # Actualizar
        campos = []
        params = {"id_hotel": id_hotel}
        
        if hotel.nombre:
            campos.append("nombre = :nombre")
            params["nombre"] = hotel.nombre
        if hotel.direccion:
            campos.append("direccion = :direccion")
            params["direccion"] = hotel.direccion
        if hotel.id_categoria:
            campos.append("id_categoria = :id_categoria")
            params["id_categoria"] = hotel.id_categoria
        
        if campos:
            query_update = f"UPDATE HOTEL SET {', '.join(campos)} WHERE id_hotel = :id_hotel"
            db.execute(text(query_update), params)
            db.commit()
        
        return obtener_hotel_por_id(id_hotel, db)
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al actualizar hotel: {str(e)}"
        )

@router.delete("/{id_hotel}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_hotel(id_hotel: int, db: Session = Depends(get_db)):
    """Eliminar un hotel"""
    try:
        query = "DELETE FROM HOTEL WHERE id_hotel = :id_hotel"
        result = db.execute(text(query), {"id_hotel": id_hotel})
        db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Hotel no encontrado"
            )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar hotel: {str(e)}"
        )

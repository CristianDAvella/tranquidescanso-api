from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from database import get_db
from schemas.registro_hospedaje_schema import (
    RegistroHospedajeCreate,
    RegistroHospedajeCheckOut,
    RegistroHospedajeResponse,
    RegistroHospedajeListResponse
)

router = APIRouter(prefix="/registro-hospedaje", tags=["registro_hospedaje"])

@router.post("/", response_model=RegistroHospedajeResponse, status_code=status.HTTP_201_CREATED)
def crear_registro_hospedaje(registro: RegistroHospedajeCreate, db: Session = Depends(get_db)):
    """Registrar check-in de un huésped"""
    try:
        # Verificar que el huésped existe
        query = "SELECT numero_id, tipo_id FROM HUESPED WHERE numero_id = :numero_id"
        huesped = db.execute(text(query), {"numero_id": registro.id_huesped}).fetchone()
        if not huesped:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Huésped no encontrado"
            )
        
        # Crear registro
        query = """
        INSERT INTO REGISTRO_HOSPEDAJE (id_reserva, id_huesped, id_habitacion,
                                        fecha_hora_checkin, responsable, mascota)
        VALUES (:id_reserva, :id_huesped, :id_habitacion, NOW(),
                :responsable, :mascota)
        RETURNING id_registro
        """
        result = db.execute(text(query), {
            "id_reserva": registro.id_reserva,
            "id_huesped": registro.id_huesped,
            "id_habitacion": registro.id_habitacion,
            "responsable": registro.responsable,
            "mascota": registro.mascota
        })
        id_registro = result.scalar()
        db.commit()
        
        return obtener_registro_por_id(id_registro, db)
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear registro: {str(e)}"
        )

@router.get("/", response_model=List[RegistroHospedajeListResponse])
def listar_registros_hospedaje(
    solo_activos: bool = True,
    db: Session = Depends(get_db)
):
    """Listar registros de hospedaje"""
    try:
        query = """
        SELECT rh.id_registro, rh.id_reserva, h.nombre, ha.numero_habitacion,
               rh.fecha_hora_checkin, rh.fecha_checkout, rh.responsable, rh.mascota
        FROM REGISTRO_HOSPEDAJE rh
        INNER JOIN HUESPED h ON rh.id_huesped = h.numero_id
        INNER JOIN HABITACION ha ON rh.id_habitacion = ha.id_habitacion
        """
        
        if solo_activos:
            query += " WHERE rh.fecha_checkout IS NULL"
        
        query += " ORDER BY rh.fecha_hora_checkin DESC"
        result = db.execute(text(query)).fetchall()
        
        return [
            {
                "id_registro": row[0],
                "id_reserva": row[1],
                "nombre_huesped": row[2],
                "numero_habitacion": row[3],
                "fecha_hora_checkin": row[4],
                "fecha_checkout": row[5],
                "responsable": row[6],
                "mascota": row[7]
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar registros: {str(e)}"
        )

@router.get("/{id_registro}", response_model=RegistroHospedajeResponse)
def obtener_registro_por_id(id_registro: int, db: Session = Depends(get_db)):
    """Obtener un registro de hospedaje por ID"""
    try:
        query = """
        SELECT id_registro, id_reserva, id_huesped, id_habitacion,
               fecha_hora_checkin, fecha_checkout, responsable, mascota
        FROM REGISTRO_HOSPEDAJE WHERE id_registro = :id_registro
        """
        registro = db.execute(text(query), {"id_registro": id_registro}).fetchone()
        
        if not registro:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro no encontrado"
            )
        
        # Verificar si es menor de edad
        query_tipo = "SELECT tipo_id FROM HUESPED WHERE numero_id = :numero_id"
        tipo_id = db.execute(text(query_tipo), {"numero_id": registro[2]}).scalar()
        es_menor = tipo_id == "Tarjeta de Identidad"
        
        return {
            "id_registro": registro[0],
            "id_reserva": registro[1],
            "id_huesped": registro[2],
            "id_habitacion": registro[3],
            "fecha_hora_checkin": registro[4],
            "fecha_checkout": registro[5],
            "responsable": registro[6],
            "mascota": registro[7],
            "es_menor_edad": es_menor
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener registro: {str(e)}"
        )

@router.post("/{id_registro}/checkout", response_model=dict)
def registrar_checkout(id_registro: int, checkout_data: RegistroHospedajeCheckOut, db: Session = Depends(get_db)):
    """Registrar check-out de un huésped"""
    try:
        query = """
        UPDATE REGISTRO_HOSPEDAJE
        SET fecha_checkout = :fecha_checkout
        WHERE id_registro = :id_registro
        """
        result = db.execute(text(query), {
            "fecha_checkout": checkout_data.fecha_checkout,
            "id_registro": id_registro
        })
        db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Registro no encontrado"
            )
        
        return {"id_registro": id_registro, "checkout_registrado": True}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al registrar checkout: {str(e)}"
        )

@router.get("/huespedes/menores-edad/", response_model=List[dict])
def listar_huespedes_menores_hospedados(db: Session = Depends(get_db)):
    """Listar huéspedes menores de edad actualmente hospedados"""
    try:
        query = """
        SELECT DISTINCT h.numero_id, h.nombre, rh.numero_habitacion
        FROM HUESPED h
        INNER JOIN REGISTRO_HOSPEDAJE rh ON h.numero_id = rh.id_huesped
        INNER JOIN HABITACION ha ON rh.id_habitacion = ha.id_habitacion
        WHERE h.tipo_id = 'Tarjeta de Identidad'
        AND rh.fecha_checkout IS NULL
        """
        result = db.execute(text(query)).fetchall()
        
        return [
            {"numero_id": row[0], "nombre": row[1], "numero_habitacion": row[2]}
            for row in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar menores: {str(e)}"
        )

@router.get("/mascotas/hospedajes-activos/", response_model=List[dict])
def listar_hospedajes_con_mascotas(db: Session = Depends(get_db)):
    """Listar huéspedes con mascotas actualmente hospedados"""
    try:
        query = """
        SELECT rh.id_registro, h.nombre, ha.numero_habitacion, rh.fecha_hora_checkin
        FROM REGISTRO_HOSPEDAJE rh
        INNER JOIN HUESPED h ON rh.id_huesped = h.numero_id
        INNER JOIN HABITACION ha ON rh.id_habitacion = ha.id_habitacion
        WHERE rh.mascota = TRUE
        AND rh.fecha_checkout IS NULL
        """
        result = db.execute(text(query)).fetchall()
        
        return [
            {
                "id_registro": row[0],
                "nombre_huesped": row[1],
                "numero_habitacion": row[2],
                "fecha_checkin": row[3]
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar mascot: {str(e)}"
        )

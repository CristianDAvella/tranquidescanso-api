from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from database import get_db
from schemas.reserva_schema import (
    ReservaCreate,
    ReservaUpdate,
    ReservaResponse,
    ReservaListResponse,
    EstadoReservaUpdate
)

router = APIRouter(prefix="/reservas", tags=["reservas"])

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
def crear_reserva(reserva: ReservaCreate, db: Session = Depends(get_db)):
    """Crear una nueva reserva"""
    try:
        # Validar que las habitaciones estén disponibles
        for id_habitacion in reserva.id_habitaciones:
            query = "SELECT ocupado FROM HABITACION WHERE id_habitacion = :id_habitacion"
            resultado = db.execute(text(query), {"id_habitacion": id_habitacion}).fetchone()
            if not resultado:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Habitación {id_habitacion} no encontrada"
                )
            if resultado[0]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Habitación {id_habitacion} ya está ocupada"
                )
        
        # Crear reserva
        query = """
        INSERT INTO RESERVA (fecha_reserva, fecha_inicio, fecha_fin, cantidad_personas, 
                            anticipo_pagado, vencimiento_reserva, id_agencia)
        VALUES (:fecha_reserva, :fecha_inicio, :fecha_fin, :cantidad_personas,
                FALSE, :vencimiento_reserva, :id_agencia)
        RETURNING id_reserva
        """
        result = db.execute(text(query), {
            "fecha_reserva": date.today(),
            "fecha_inicio": reserva.fecha_inicio,
            "fecha_fin": reserva.fecha_fin,
            "cantidad_personas": reserva.cantidad_personas,
            "vencimiento_reserva": reserva.vencimiento_reserva,
            "id_agencia": reserva.id_agencia
        })
        id_reserva = result.scalar()
        
        # Asociar habitaciones a la reserva
        for id_habitacion in reserva.id_habitaciones:
            query_hab = """
            INSERT INTO HABITACION_RESERVA (id_habitacion, id_reserva)
            VALUES (:id_habitacion, :id_reserva)
            """
            db.execute(text(query_hab), {"id_habitacion": id_habitacion, "id_reserva": id_reserva})
            
            # Marcar habitación como ocupada
            query_update = "UPDATE HABITACION SET ocupado = TRUE WHERE id_habitacion = :id_habitacion"
            db.execute(text(query_update), {"id_habitacion": id_habitacion})
        
        # Asociar servicios a la reserva
        for id_servicio in reserva.servicios:
            query_serv = """
            INSERT INTO RESERVA_SERVICIO (id_reserva, id_servicio)
            VALUES (:id_reserva, :id_servicio)
            """
            db.execute(text(query_serv), {"id_reserva": id_reserva, "id_servicio": id_servicio})
        
        # Registrar estado inicial
        query_estado = """
        INSERT INTO ESTADO_RESERVA (id_reserva, estado)
        VALUES (:id_reserva, 'Confirmada')
        """
        db.execute(text(query_estado), {"id_reserva": id_reserva})
        
        db.commit()
        return {"id_reserva": id_reserva, "mensaje": "Reserva creada exitosamente"}
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al crear reserva: {str(e)}"
        )

@router.get("/", response_model=List[ReservaListResponse])
def listar_reservas(
    filtro_estado: Optional[str] = None,
    filtro_fecha_inicio: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """Listar reservas con filtros opcionales"""
    try:
        query = """
        SELECT DISTINCT r.id_reserva, r.fecha_inicio, r.fecha_fin, r.cantidad_personas,
               r.anticipo_pagado, er.estado
        FROM RESERVA r
        LEFT JOIN ESTADO_RESERVA er ON r.id_reserva = er.id_reserva
        WHERE er.id_estado = (
            SELECT MAX(id_estado) FROM ESTADO_RESERVA WHERE id_reserva = r.id_reserva
        )
        """
        
        params = {}
        if filtro_estado:
            query += " AND er.estado = :estado"
            params["estado"] = filtro_estado
        if filtro_fecha_inicio:
            query += " AND r.fecha_inicio >= :fecha_inicio"
            params["fecha_inicio"] = filtro_fecha_inicio
        
        query += " ORDER BY r.fecha_inicio DESC"
        result = db.execute(text(query), params).fetchall()
        
        return [
            {
                "id_reserva": row[0],
                "fecha_inicio": row[1],
                "fecha_fin": row[2],
                "cantidad_personas": row[3],
                "anticipo_pagado": row[4],
                "estado_actual": row[5]
            }
            for row in result
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al listar reservas: {str(e)}"
        )

@router.get("/{id_reserva}", response_model=dict)
def obtener_reserva_por_id(id_reserva: int, db: Session = Depends(get_db)):
    """Obtener una reserva completa por ID"""
    try:
        # Obtener datos básicos
        query = """
        SELECT id_reserva, fecha_reserva, fecha_inicio, fecha_fin, cantidad_personas,
               anticipo_pagado, vencimiento_reserva, id_agencia
        FROM RESERVA WHERE id_reserva = :id_reserva
        """
        reserva = db.execute(text(query), {"id_reserva": id_reserva}).fetchone()
        
        if not reserva:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        
        # Obtener habitaciones
        query_hab = """
        SELECT h.id_habitacion, h.numero_habitacion, th.descripcion
        FROM HABITACION h
        INNER JOIN TIPO_HABITACION th ON h.id_tipo = th.id_tipo
        INNER JOIN HABITACION_RESERVA hr ON h.id_habitacion = hr.id_habitacion
        WHERE hr.id_reserva = :id_reserva
        """
        habitaciones = db.execute(text(query_hab), {"id_reserva": id_reserva}).fetchall()
        
        # Obtener servicios
        query_serv = """
        SELECT s.id_servicio, s.nombre, s.costo
        FROM SERVICIO_ADICIONAL s
        INNER JOIN RESERVA_SERVICIO rs ON s.id_servicio = rs.id_servicio
        WHERE rs.id_reserva = :id_reserva
        """
        servicios = db.execute(text(query_serv), {"id_reserva": id_reserva}).fetchall()
        
        # Obtener estado actual
        query_estado = """
        SELECT estado FROM ESTADO_RESERVA
        WHERE id_reserva = :id_reserva
        ORDER BY id_estado DESC LIMIT 1
        """
        estado = db.execute(text(query_estado), {"id_reserva": id_reserva}).fetchone()
        
        return {
            "id_reserva": reserva[0],
            "fecha_reserva": reserva[1],
            "fecha_inicio": reserva[2],
            "fecha_fin": reserva[3],
            "cantidad_personas": reserva[4],
            "anticipo_pagado": reserva[5],
            "vencimiento_reserva": reserva[6],
            "id_agencia": reserva[7],
            "habitaciones": [{"id": h[0], "numero": h[1], "tipo": h[2]} for h in habitaciones],
            "servicios": [{"id": s[0], "nombre": s[1], "costo": s[2]} for s in servicios],
            "estado_actual": estado[0] if estado else "Sin estado"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener reserva: {str(e)}"
        )

@router.put("/{id_reserva}/estado", response_model=dict)
def cambiar_estado_reserva(id_reserva: int, cambio: EstadoReservaUpdate, db: Session = Depends(get_db)):
    """Cambiar el estado de una reserva (Confirmada, Cancelada, No Presentada, Completada)"""
    try:
        # Verificar reserva existe
        query = "SELECT id_reserva FROM RESERVA WHERE id_reserva = :id_reserva"
        if not db.execute(text(query), {"id_reserva": id_reserva}).fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        
        # Registrar nuevo estado
        query_estado = """
        INSERT INTO ESTADO_RESERVA (id_reserva, estado)
        VALUES (:id_reserva, :estado)
        """
        db.execute(text(query_estado), {"id_reserva": id_reserva, "estado": cambio.estado})
        
        # Si es cancelada, liberar habitaciones
        if cambio.estado == "Cancelada":
            query_hab = """
            SELECT id_habitacion FROM HABITACION_RESERVA WHERE id_reserva = :id_reserva
            """
            habitaciones = db.execute(text(query_hab), {"id_reserva": id_reserva}).fetchall()
            for hab in habitaciones:
                query_update = "UPDATE HABITACION SET ocupado = FALSE WHERE id_habitacion = :id_habitacion"
                db.execute(text(query_update), {"id_habitacion": hab[0]})
        
        db.commit()
        return {"id_reserva": id_reserva, "nuevo_estado": cambio.estado}
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al cambiar estado: {str(e)}"
        )

@router.put("/{id_reserva}/anticipo", response_model=dict)
def registrar_pago_anticipo(id_reserva: int, db: Session = Depends(get_db)):
    """Registrar que se pagó el anticipo (20%)"""
    try:
        query = "UPDATE RESERVA SET anticipo_pagado = TRUE WHERE id_reserva = :id_reserva"
        result = db.execute(text(query), {"id_reserva": id_reserva})
        db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        
        return {"id_reserva": id_reserva, "anticipo_pagado": True}
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al registrar pago: {str(e)}"
        )

@router.delete("/{id_reserva}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_reserva(id_reserva: int, db: Session = Depends(get_db)):
    """Eliminar una reserva (cancela y libera habitaciones)"""
    try:
        # Liberar habitaciones
        query_hab = """
        SELECT id_habitacion FROM HABITACION_RESERVA WHERE id_reserva = :id_reserva
        """
        habitaciones = db.execute(text(query_hab), {"id_reserva": id_reserva}).fetchall()
        for hab in habitaciones:
            query_update = "UPDATE HABITACION SET ocupado = FALSE WHERE id_habitacion = :id_habitacion"
            db.execute(text(query_update), {"id_habitacion": hab[0]})
        
        # Eliminar reserva
        query = "DELETE FROM RESERVA WHERE id_reserva = :id_reserva"
        result = db.execute(text(query), {"id_reserva": id_reserva})
        db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al eliminar reserva: {str(e)}"
        )

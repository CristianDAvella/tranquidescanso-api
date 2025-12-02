from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

class ReservaBase(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    cantidad_personas: int
    vencimiento_reserva: datetime
    id_agencia: Optional[int] = None

class ReservaCreate(ReservaBase):
    id_habitaciones: List[int]  # IDs de habitaciones a reservar
    servicios: Optional[List[int]] = []  # IDs de servicios adicionales

class ReservaUpdate(BaseModel):
    cantidad_personas: Optional[int] = None
    anticipo_pagado: Optional[bool] = None
    id_agencia: Optional[int] = None

class ReservaResponse(ReservaBase):
    id_reserva: int
    fecha_reserva: date
    anticipo_pagado: bool
    habitaciones: List[dict]
    servicios: List[dict]
    estado_actual: str
    
    class Config:
        from_attributes = True

class ReservaListResponse(BaseModel):
    id_reserva: int
    fecha_inicio: date
    fecha_fin: date
    cantidad_personas: int
    anticipo_pagado: bool
    estado_actual: str
    
    class Config:
        from_attributes = True

class PagarAnticipoRequest(BaseModel):
    id_reserva: int
    monto: Decimal

class EstadoReservaUpdate(BaseModel):
    estado: str  # "Confirmada", "Cancelada", "No Presentada", "Completada"

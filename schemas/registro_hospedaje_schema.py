from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

class RegistroHospedajeBase(BaseModel):
    id_reserva: int
    id_huesped: str
    id_habitacion: int
    responsable: bool = False
    mascota: bool = False

class RegistroHospedajeCreate(RegistroHospedajeBase):
    pass

class RegistroHospedajeCheckOut(BaseModel):
    fecha_checkout: date

class RegistroHospedajeResponse(RegistroHospedajeBase):
    id_registro: int
    fecha_hora_checkin: datetime
    fecha_checkout: Optional[date]
    es_menor_edad: bool  # Deducido de HUESPED.Tipo_id
    
    class Config:
        from_attributes = True

class RegistroHospedajeListResponse(BaseModel):
    id_registro: int
    id_reserva: int
    nombre_huesped: str
    numero_habitacion: int
    fecha_hora_checkin: datetime
    fecha_checkout: Optional[date]
    responsable: bool
    mascota: bool
    
    class Config:
        from_attributes = True

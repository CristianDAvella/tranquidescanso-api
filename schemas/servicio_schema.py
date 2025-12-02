from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class ServicioBase(BaseModel):
    nombre: str
    costo: Decimal

class ServicioCreate(ServicioBase):
    pass

class ServicioUpdate(BaseModel):
    nombre: Optional[str] = None
    costo: Optional[Decimal] = None

class ServicioResponse(ServicioBase):
    id_servicio: int
    
    class Config:
        from_attributes = True

class ServicioListResponse(BaseModel):
    id_servicio: int
    nombre: str
    costo: Decimal
    
    class Config:
        from_attributes = True

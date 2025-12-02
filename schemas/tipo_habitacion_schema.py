from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class TipoHabitacionBase(BaseModel):
    descripcion: str
    capacidad: int
    valor: Decimal

class TipoHabitacionCreate(TipoHabitacionBase):
    pass

class TipoHabitacionUpdate(BaseModel):
    descripcion: Optional[str] = None
    capacidad: Optional[int] = None
    valor: Optional[Decimal] = None

class TipoHabitacionResponse(TipoHabitacionBase):
    id_tipo: int
    
    class Config:
        from_attributes = True

class TipoHabitacionListResponse(BaseModel):
    id_tipo: int
    descripcion: str
    capacidad: int
    valor: Decimal
    
    class Config:
        from_attributes = True

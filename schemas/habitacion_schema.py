from pydantic import BaseModel
from typing import Optional

class HabitacionBase(BaseModel):
    numero_habitacion: int
    id_hotel: int
    id_tipo: int
    ocupado: bool = False

class HabitacionCreate(HabitacionBase):
    pass

class HabitacionUpdate(BaseModel):
    numero_habitacion: Optional[int] = None
    ocupado: Optional[bool] = None

class HabitacionResponse(HabitacionBase):
    id_habitacion: int
    
    class Config:
        from_attributes = True

class HabitacionListResponse(BaseModel):
    id_habitacion: int
    numero_habitacion: int
    nombre_hotel: str
    tipo_habitacion: str
    ocupado: bool
    
    class Config:
        from_attributes = True

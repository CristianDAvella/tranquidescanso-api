from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class TelefonoHotelBase(BaseModel):
    telefono: str

class HotelBase(BaseModel):
    nombre: str
    direccion: str
    anio_inauguracion: int
    id_categoria: int = 1  # Por defecto, categoría 1

class HotelCreate(HotelBase):
    telefonos: List[str] = []

class HotelUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None
    id_categoria: Optional[int] = None

class HotelResponse(HotelBase):
    id_hotel: int
    telefonos: List[str]
    
    class Config:
        from_attributes = True

class HotelListResponse(BaseModel):
    id_hotel: int
    nombre: str
    direccion: str
    anio_inauguracion: int
    
    class Config:
        from_attributes = True

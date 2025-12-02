from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional

class TelefonoBase(BaseModel):
    telefono: str

class HuespedBase(BaseModel):
    numero_id: str
    tipo_id: str  # "Cédula", "Pasaporte", "RUT", "Tarjeta de Identidad"
    nombre: str
    direccion: str


class HuespedCreate(HuespedBase):
    telefonos: List[str] = []  # Lista de teléfonos a crear

class HuespedUpdate(BaseModel):
    nombre: Optional[str] = None
    direccion: Optional[str] = None


class HuespedResponse(HuespedBase):
    telefonos: List[str]
    
    class Config:
        from_attributes = True

class HuespedListResponse(BaseModel):
    numero_id: str
    nombre: str
    tipo_id: str
    
    class Config:
        from_attributes = True

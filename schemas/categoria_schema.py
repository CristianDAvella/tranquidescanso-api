from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CategoriaBase(BaseModel):
    nombre_categoria: str

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre_categoria: Optional[str] = None

class CategoriaResponse(CategoriaBase):
    id_categoria: int
    fecha_cambio: datetime
    
    class Config:
        from_attributes = True

class CategoriaListResponse(BaseModel):
    id_categoria: int
    nombre_categoria: str
    fecha_cambio: datetime
    
    class Config:
        from_attributes = True

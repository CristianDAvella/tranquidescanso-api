from pydantic import BaseModel
from typing import Optional

class AgenciaBase(BaseModel):
    nombre: str

class AgenciaCreate(AgenciaBase):
    pass

class AgenciaUpdate(BaseModel):
    nombre: Optional[str] = None

class AgenciaResponse(AgenciaBase):
    id_agencia: int
    
    class Config:
        from_attributes = True

class AgenciaListResponse(BaseModel):
    id_agencia: int
    nombre: str
    
    class Config:
        from_attributes = True

from pydantic import BaseModel

class RefDataCreate(BaseModel):
    name: str

class RefDataOut(BaseModel):
    id: int
    name: str

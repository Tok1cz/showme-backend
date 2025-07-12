from pydantic import BaseModel

class RefDataOut(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True
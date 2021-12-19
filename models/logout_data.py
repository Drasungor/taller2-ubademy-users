from pydantic import BaseModel

class Logout(BaseModel):
    email: str

from pydantic import BaseModel

class RegistrationData(BaseModel):
    email: str
    password: str
    name: str
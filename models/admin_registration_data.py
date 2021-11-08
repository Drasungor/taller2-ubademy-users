from pydantic import BaseModel

class AdminRegistrationData(BaseModel):
    email: str
    password: str
    name: str
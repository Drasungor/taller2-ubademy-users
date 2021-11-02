from pydantic import BaseModel

class AdminRegistrationData(BaseModel):
    username: str
    email: str
    password: str
    name: str
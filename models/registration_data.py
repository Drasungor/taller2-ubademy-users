from pydantic import BaseModel

class RegistrationData(BaseModel):
    email: str
    password: str
    expo_token: str
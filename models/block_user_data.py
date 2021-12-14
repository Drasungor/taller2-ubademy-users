from pydantic import BaseModel

class BlockUserData(BaseModel):
    modified_user: str
    is_blocked: bool
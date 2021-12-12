from pydantic import BaseModel

class BlockUserData(BaseModel):
    is_admin: bool
    modified_user: str
    is_blocked: bool
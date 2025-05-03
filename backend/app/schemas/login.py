from pydantic import BaseModel

class LoginBase(BaseModel):
    email: str
    password: str

class LoginRequest(LoginBase):
    pass

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
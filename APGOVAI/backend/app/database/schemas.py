from pydantic import BaseModel


class LoginRequest(BaseModel):

    username: str

    password: str


class LoginResponse(BaseModel):

    access_token: str

    token_type: str

    role: str


class UserCreate(BaseModel):

    username: str

    password: str

    role: str = "user"


class UserResponse(BaseModel):

    id: str

    username: str

    role: str

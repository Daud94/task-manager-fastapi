from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str

    class Config:
        orm_mode = True


class CreateUser(UserBase):
    password: str


class UserLogin(UserBase):
    pass

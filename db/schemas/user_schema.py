from pydantic import BaseModel, EmailStr, ConfigDict

class UserBaseInput(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str

class UserBaseOut(UserBaseInput):
    pass

class CreateUser(UserBaseInput):
    password: str


class UserLogin(UserBaseInput):
    pass

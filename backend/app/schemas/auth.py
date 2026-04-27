from pydantic import BaseModel, EmailStr

class SignupInitiate(BaseModel):
    phone: str


class SignupVerify(BaseModel):
    phone: str
    otp: str


class SignupComplete(BaseModel):
    email: EmailStr
    password: str
    phone: str
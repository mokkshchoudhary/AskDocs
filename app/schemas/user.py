from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    password: str | None = None

class UserOut(UserBase):
    id: int
    
    class Config:
        from_attributes = True

class UserInDB(UserOut):
    hashed_password: str

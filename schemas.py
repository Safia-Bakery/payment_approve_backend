from pydantic import BaseModel
from fastapi import Form,UploadFile,File
from typing import Optional
class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str


class TokenRequest(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str



class CategoryCreate(BaseModel):
    name :str



class Create_Order(BaseModel):
    category_id :int
    purchaser:str
    product:str
    seller:str
    delivery_time:str
    price: float
    payer :str
    urgent:Optional[bool]=False
    description: str
    payment_type:str
    image_id:Optional[int]=None




class UpdateUserRole(BaseModel):
    role : str
    user_id: int



class User(BaseModel):
    id: int
    username: str
    role: str

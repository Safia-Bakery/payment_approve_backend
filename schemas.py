from pydantic import BaseModel
from fastapi import Form,UploadFile,File
from typing import Optional
class UserBase(BaseModel):
    username: str
    full_name: Optional[str]=None
    telegram_id : int


class UserCreate(UserBase):
    password: str


class TokenRequest(BaseModel):
    username: str
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
    success:Optional[str]=True


class GetCategoryWithId(BaseModel): 
    category :str
    purchaser:str
    product:str
    seller:str
    delivery_time:str
    price: float
    payer :str
    urgent:Optional[bool]=False
    description: str
    payment_type:str
    image:Optional[str]=None


class GetTelId(BaseModel):
    id:int


class TelAcceptReject(BaseModel):
    telid : int
    status : str
    order_id: int
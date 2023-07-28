from pydantic import BaseModel
from fastapi import Form,UploadFile,File
from typing import Optional
from datetime import datetime
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
    user_id:int




class UpdateUserRole(BaseModel):
    role : str
    user_id: int



class User(BaseModel):
    id: int
    username: str
    role: str
    success:Optional[str]=True
    full_name:Optional[str]=None
    class Config:
        from_attributes=True


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
    image:Optional[int]=None
    amount_paid:Optional[float]=0
    nakladnoy:Optional[str]=None


class GetTelId(BaseModel):
    id:int


class TelAcceptReject(BaseModel):
    telid : int
    status : str
    order_id: int


class Image_url_schema(BaseModel):
    image_url:str
    class Config:
        from_attributes=True

class GetCategoryAsPaginated(BaseModel): 
    category :CategoryCreate
    purchaser:str
    product:str
    seller:str
    delivery_time:str
    price: float
    payer :str
    urgent:bool
    description: str
    payment_type:str
    image:Optional[Image_url_schema]=None
    time_created: datetime
    amount_paid:Optional[float]=0
    nakladnoy:Optional[str]=None
    id : int
    status:str
    class Config:
        from_attributes=True


class OrderAddPaid(BaseModel):
    paid_amount:Optional[float]=None
    nakladnoy:Optional[str]=None
    order_id:int
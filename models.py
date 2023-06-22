from sqlalchemy import Column, Integer, String,ForeignKey,Float,DateTime,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
Base = declarative_base()
from datetime import datetime
import pytz 
timezonetash = pytz.timezone("Asia/Tashkent") 

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String,default='unconfirmed',unique=True)
    time_created = Column(DateTime,default=datetime.now(timezonetash))
    userhistory = relationship('UserHistory',back_populates='user')
    




class Category(Base):   
    __tablename__='category'
    id = Column(Integer,primary_key=True,index=True)
    name = Column(String,index=True,unique=True)
    order = relationship('Order',back_populates='category')




class Order(Base):
    __tablename__='order'
    id = Column(Integer,primary_key=True,index=True)
    category = relationship('Category',back_populates='order')
    category_id = Column(Integer,ForeignKey('category.id'))
    purchaser = Column(String,index=True)
    product = Column(String,index=True)
    seller = Column(String,index=True)
    delivery_time = Column(String,index=True)
    price = Column(Float)
    payer = Column(String)
    status = Column(String,default='musa')
    userhistory = relationship('UserHistory',back_populates='order')
    time_created = Column(DateTime,default=datetime.now(timezonetash))
    urgent = Column(Boolean,default=False)
    image_url = relationship('ImageUpload',back_populates='order_image')
    image_id = Column(Integer,ForeignKey('images.id'),nullable=True)
    description = Column(String,nullable=True)
    payment_type = Column(String)
    




class UserHistory(Base):
    __tablename__='userhistory'
    id = Column(Integer,primary_key=True,index=True)
    order_id = Column(Integer,ForeignKey('order.id'))
    order = relationship('Order',back_populates='userhistory')
    user_id = Column(Integer,ForeignKey('users.id'))
    user = relationship('User',back_populates='userhistory')
    time_created = Column(DateTime,default=datetime.now(timezonetash))


class ImageUpload(Base):
    __tablename__='images'
    id = Column(Integer,primary_key=True,index=True)
    image_url = Column(String)
    order_image = relationship('Order',back_populates='image_url')




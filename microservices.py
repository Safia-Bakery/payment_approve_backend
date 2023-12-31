from datetime import datetime,timedelta
import pytz
from jose import jwt
from passlib.context import CryptContext
import requests
import bcrypt
tashkentimezone = pytz.timezone('Asia/Tashkent')

def create_access_token(data: dict):
    SECRET_KEY = "thisistokenforusersecretauth"  # Replace with your own secret key
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 3000000 

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))




###########################new test
from datetime import datetime, timedelta
from typing import Union, Any
from jose import jwt


ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = 'thisistokenforusersecretauth'   # should be kept secret
JWT_REFRESH_SECRET_KEY =  'thisistokenforusersecretrefresh'   # should be kept secret



def create_access_token2(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt



def create_refresh_token2(subject: Union[str, Any], expires_delta: int = None) -> str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



def get_hashed_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password, hashed_pass)


def sendtotelegram(bot_token,chat_id,message_text):
    keyboard = {
        'inline_keyboard': [
            [{'text': 'Yes', 'callback_data': 'accepted'}],
            [{'text': 'No', 'callback_data': 'denied'}]
        ]
    }

    # Create the request payload
    payload = {
        'chat_id': chat_id,
        'text': message_text,
        'reply_markup': keyboard,
        'parse_mode': 'HTML'
    }

    # Send the request to send the inline keyboard message
    response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json=payload,)

    # Check the response status
    if response.status_code == 200:
        return response
    else:
        return False
    
def sendtotelegramchannel(bot_token,chat_id,message_text):

    # Create the request payload
    payload = {
        'chat_id': chat_id,
        'text': message_text,
        'parse_mode': 'HTML'
    }

    # Send the request to send the inline keyboard message
    response = requests.post(f'https://api.telegram.org/bot{bot_token}/sendMessage', json=payload,)

    # Check the response status
    if response.status_code == 200:
        return response
    else:
        return False
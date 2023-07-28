from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException,UploadFile,File,Form,Header,Request,status
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from microservices import create_access_token2,create_refresh_token2
import shutil
import crud
from typing import Union, Any
from pydantic import ValidationError
import models 
import microservices
import schemas
from fastapi_pagination import Page,paginate,add_pagination

from database import engine,SessionLocal
from microservices import create_access_token,verify_password
from typing import Optional,Annotated
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
CHANNEL_id = '-1001965707394'
models.Base.metadata.create_all(bind=engine)
import bcrypt
app = FastAPI()
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = 'thisistokenforusersecretauth'   # should be kept secret
JWT_REFRESH_SECRET_KEY =  'thisistokenforusersecretrefresh'

BOT_TOKEN = '6298581686:AAGVha0x_j3u-KPik0NDW6eSd_LBZ-0yQRI'

origins = ["*"]


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login/2",
    scheme_name="JWT"
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



async def get_current_user(token: str = Depends(reuseable_oauth),db:Session=Depends(get_db)) -> schemas.User:
    try:
        payload = jwt.decode(
            token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
        )
        expire_date = payload.get('exp')
        sub = payload.get('sub')
        if datetime.fromtimestamp(expire_date) < datetime.now():
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except(jwt.JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user: Union[dict[str, Any], None] = crud.get_user(db,   sub)
    
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not find user",
        )
    
    return user

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/register",response_model_include=['username','status','id'])
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    username = str(user.username).replace('+','')
    db_user = crud.get_user(db, username=username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user,username=username)




@app.post("/login")
async def generate_token(form_data: schemas.TokenRequest, db: Session = Depends(get_db)):
    username = str(form_data.username).replace('+','')
    user = crud.get_user(db, username=username)
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    elif not verify_password(form_data.password, user.hashed_password): 
        raise HTTPException(status_code=400, detail="Invalid username or password")
    if user.role not in ['musa','shakhzod','begzod','fin','accountant','purchasing','superadmin','nakladnoy']:
        raise HTTPException(status_code=400, detail="You are not super user")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer",'status_user':user.role,'success':True}



@app.post('/create/category')
async def creaet_category(form_data:schemas.CategoryCreate,db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    return crud.create_category(db,name=form_data.name)


@app.get('/get/list/category')
async def get_category(db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    return crud.get_category_list(db=db)


@app.post('/create/order',response_model_include=['id',])
async def create_order(form:schemas.Create_Order,db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    if request_user.role in ['purchasing','superadmin']:
        try:
            data = crud.create_order(db,order=form)
            nakladnoy = crud.get_user_with_idcr(db=db,user_id=form.user_id)
            if nakladnoy.role == 'unconfirmed':
                crud.update_role(db=db,user_id=form.user_id,role = 'nakladnoy')
        except:
            return {'message':'telegram id is not valid so change it','success':False}
        try:
            datetime_object = datetime.strptime(data.delivery_time, "%Y-%m-%dT%H:%M:%S.%fZ")
            year = datetime_object.strftime("%Y")
            month = datetime_object.strftime("%m")
            day = datetime_object.strftime("%d")
            hours = datetime_object.strftime("%H")
            minutes = datetime_object.strftime("%M")
            dateandtime = f"{year}-{month}-{day}, {hours}:{minutes}"
            message= f"Заявка № {data.id}\n🔘Тип: {data.category.name}\n🙍‍♂Заказчик: {data.purchaser}\n📦Товар: {data.product}\n👨‍💼Поставщик: {data.seller}\n🕘Срок: {dateandtime}\n💰Стоимость: {data.price}\n💲Тип оплаты: {data.payment_type}\n💳Плательщик: {data.payer}"
            user = crud.get_one_user_with_role(db,'musa')


            response = microservices.sendtotelegram(bot_token=BOT_TOKEN,chat_id=user.telegram_id,message_text=message)
        except:
            return {'success':True,'messaged':'order created but got some issues while sending it to telegram'}
    else:
        return {'message':'you are not superadmin or purchasing so you cannot create order','success':False}
    return data

@app.post('/image/upload',response_model_include=['id'])
async def create_order(image:UploadFile,db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    with open(f"uploads/{image.filename}", 'wb') as f:
        shutil.copyfileobj(image.file,f)
    
    return crud.create_image(db,image_url=f"uploads/{image.filename}")

list_of_roles = {'musa':'Руководитель отдела закупа',
                'shakhzod':'Директор производства',
                'begzod':'Директор розницы',
                'fin':'Финансовый отдел',
                'accountant':'Бухгалтерия',
                'unconfirmed':'Роль не выбран',
                'purchasing':'Отдел закупа'}


@app.put('/update/user/role')
async def update_user_role(form:schemas.UpdateUserRole,db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    if request_user.role == 'superadmin':
        try:
            data = crud.update_role(db=db,user_id=form.user_id,role=form.role)

        except:
            return {'message':'couldnot found user or the user with this role already exist'}
        if not data:
            return {'message':'couldnot found user or the user with this role already existwer'}
        microservices.sendtotelegramchannel(bot_token=BOT_TOKEN,chat_id=data.telegram_id,message_text=f"Ваш аккаунт активирован. Вы назначены на роль: {list_of_roles[str(data.role)]}")
        return data
    else:
        return {'message':'you arenot super user ','status':False}



@app.get('/get/user/list/with/role',response_model_exclude=['id',],)
async def get_user_list(db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    data  = crud.get_user_list(db=db)
    return data


@app.get('/get/order/list',response_model=Page[schemas.GetCategoryAsPaginated])
async def get_order_list(db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):

    order = crud.get_order_list(db=db,role = request_user.role,user_id=request_user.id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="not found exceptnion "
        )
    print(order)
    #print(schemas.Create_Order(data))\
    #order = [{'id':i.id,'status':i.status,'category':i.category.name , 'purchaser':i.purchaser, 'product':i.product,'seller':i.seller,'delivery_time':i.delivery_time,'price':i.price,'payer':i.payer,'urgent':i.urgent,'description':i.description,'payment_type':i.payment_type,'image_url':i.image_url} for i in order ]
    return paginate(order)

@app.get('/get/list/of/roles')
async def get_roles(request_user: schemas.User = Depends(get_current_user)):
    return {'success':True,'listroles':list_of_roles}

@app.get('/get/user/with/id/{id_user}',)
async def get_user_with_id(id_user:int,db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    user = crud.get_user_with_idcr(db=db,user_id=id_user)
    if not user:
        return {'message':'user with this id not exist'}
    return user



@app.get('/get/order/with/id/{id_order}')
async def get_order_with_id(id_order:int,db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    order = crud.get_order_with_id(db=db,order_id=id_order)
    if not order:
        return {"message":'order with this id doesnot exist','success':False}
    if order.image_id:
        order = schemas.GetCategoryWithId(
            category=order.category.name,
            purchaser=order.purchaser,
            product=order.product,
            seller=order.seller,
            delivery_time=order.delivery_time,
            price=order.price,
            payer=order.payer,
            urgent=order.urgent,
            description=order.description,
            payment_type=order.payment_type,
            image= order.image_url.image_url,
            amount_paid=order.amount_paid,
            nakladnoy=order.nakladnoy
        )
    else:
        order = schemas.GetCategoryWithId(
            category=order.category.name,
            purchaser=order.purchaser,
            product=order.product,
            seller=order.seller,
            delivery_time=order.delivery_time,
            price=order.price,
            payer=order.payer,
            urgent=order.urgent,
            description=order.description,
            payment_type=order.payment_type,
            image = order.image_url,
            amount_paid=order.amount_paid,
            nakladnoy=order.nakladnoy
        ) 
    return order



admindict = {
    'musa':"Тухтаев Мусажон",
    'begzod':'Самигжанов Бекзод',
    'fin':'Финансовый отдел',
    'accountant':'Бухгалтерия',
    'shakhzod':'Гафуржанов Шахзод'
}

@app.put('/order/accept/reject/{order_id}/{status}')
async def order_accept_reject(order_id:int,status:str,db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    if request_user.role not in ['musa','shakhzod','begzod','fin']:
        return {'message':'you cannot perform this action','success':False}
    data = crud.order_accept_db(db,order_id=order_id,status=status,role=request_user.role)
    datetime_object = datetime.strptime(data.delivery_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    year = datetime_object.strftime("%Y")
    month = datetime_object.strftime("%m")
    day = datetime_object.strftime("%d")
    hours = datetime_object.strftime("%H")
    minutes = datetime_object.strftime("%M")
    dateandtime = f"{year}-{month}-{day}, {hours}:{minutes}"
    if not data:
        return {'message':'you cannot vote for this order. reason you may not be owner or accaptable status are accepted,denied','success':True}
    if data.status not in['denied','paid']:
        user = crud.get_one_user_with_role(db,data.status)
        if data.status=='accountant':
            message= f"Заявка № {data.id}\n🔘Тип: {data.category.name}\n🙍‍♂Заказчик: {data.purchaser}"
            microservices.sendtotelegramchannel(bot_token=BOT_TOKEN,chat_id=user.telegram_id,message_text=message)
        else:
            message= f"Заявка № {data.id}\n🔘Тип: {data.category.name}\n🙍‍♂Заказчик: {data.purchaser}\n📦Товар: {data.product}\n👨‍💼Поставщик: {data.seller}\n🕘Срок: {dateandtime}\n💰Стоимость: {data.price} UZS\n💲Тип оплаты: {data.payment_type}\n💳Плательщик: {data.payer}\nℹ️Описание: {data.description}"

            response = microservices.sendtotelegram(bot_token=BOT_TOKEN,chat_id=user.telegram_id,message_text=message)
    if data.status == 'paid' and data.category.name=='Розница':
        message= f"Заявка № {data.id}\n\n🔘Тип: {data.category.name}\n🙍‍♂Заказчик: {data.purchaser}\n📦Товар: {data.product}\n👨‍💼Поставщик: {data.seller}\n🕘Срок: {dateandtime}\n💰Стоимость: {data.price}\n💲Тип оплаты: {data.payment_type}\n💳Плательщик: {data.payer}\nℹ️Описание: {data.description}\n📝 Комментарии: \n\nТухтаев Мусажон: Одобрено ✅\nСамигжанов Бекзод: Одобрено ✅\nФинансовый отдел: Подтвердждено ✅\nБухгалтерия: Подтвердждено ✅"
    
        response = microservices.sendtotelegramchannel(bot_token=BOT_TOKEN,chat_id=CHANNEL_id,message_text=message)
    if data.status == 'paid' and data.category.name=='Фабрика':
        message= f"Заявка № {data.id}\n\n🔘Тип: {data.category.name}\n🙍‍♂Заказчик: {data.purchaser}\n📦Товар: {data.product}\n👨‍💼Поставщик: {data.seller}\n🕘Срок: {dateandtime}\n💰Стоимость: {data.price}\n💲Тип оплаты: {data.payment_type}\n💳Плательщик: {data.payer}\nℹ️Описание: {data.description}\n📝 Комментарии: \n\nТухтаев Мусажон: Одобрено ✅\nШахзод: Одобрено ✅\nФинансовый отдел: Подтвердждено ✅\nБухгалтерия: Подтвердждено ✅"
    
        response = microservices.sendtotelegramchannel(bot_token=BOT_TOKEN,chat_id=CHANNEL_id,message_text=message)
    if data.status == 'denied':
        message= f"Заявка № {data.id}\n\n🔘Тип: {data.category.name}\n🙍‍♂Заказчик: {data.purchaser}\n📦Товар: {data.product}\n👨‍💼Поставщик: {data.seller}\n🕘Срок: {dateandtime}\n💰Стоимость: {data.price}\n💲Тип оплаты: {data.payment_type}\n💳Плательщик: {data.payer}\nℹ️Описание: {data.description}\n📝 Комментарии: \n\n{admindict[request_user.role]} ❌"
    
        response = microservices.sendtotelegramchannel(bot_token=BOT_TOKEN,chat_id=CHANNEL_id,message_text=message)
    return data



@app.get('/users/overhead',response_model=list[schemas.User])
async def get_users_for_nakladnoy(db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    users = crud.get_user_nakladnoy(db)
    return users

@app.put('/order/pay',response_model=schemas.GetCategoryAsPaginated)
async def order_add_paid_amaount(form_data:schemas.OrderAddPaid,db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    if request_user.role in ['accountant','nakladnoy']:
        data = crud.add_paid_amaunt_order(db,form_data=form_data)
        if data.status=='paid':
            message= f"Заявка № {data.id}\n🔘Тип: {data.category.name}\n🙍‍♂Заказчик: {data.purchaser}"
            microservices.sendtotelegramchannel(bot_token=BOT_TOKEN,chat_id=data.user.telegram_id,message_text=message)
            if data.category.name=='Розница':
                message= f"Заявка № {data.id}\n🔘Тип: {data.category.name}\n🙍‍♂Заказчик: {data.purchaser}\n📦Товар: {data.product}\n👨‍💼Поставщик: {data.seller}\n🕘Срок: {dateandtime}\n💰Стоимость: {data.price} UZS\n💲Тип оплаты: {data.payment_type}\n💳Плательщик: {data.payer}\nℹ️Описание: {data.description}\n📝 Комментарии: \n\nТухтаев Мусажон: Одобрено ✅\nСамигжанов Бекзод: Одобрено ✅\nФинансовый отдел: Подтвердждено ✅\nБухгалтерия: Подтвердждено ✅"
    
                response = microservices.sendtotelegramchannel(bot_token=BOT_TOKEN,chat_id=CHANNEL_id,message_text=message)
            if  data.category.name=='Фабрика':
                message= f"Заявка № {data.id}\n🔘Тип: {data.category.name}\n🙍‍♂Заказчик: {data.purchaser}\n📦Товар: {data.product}\n👨‍💼Поставщик: {data.seller}\n🕘Срок: {dateandtime}\n💰Стоимость: {data.price} UZS\n💲Тип оплаты: {data.payment_type}\n💳Плательщик: {data.payer}\nℹ️Описание: {data.description}\n📝 Комментарии: \n\nТухтаев Мусажон: Одобрено ✅\nШахзод: Одобрено ✅\nФинансовый отдел: Подтвердждено ✅\nБухгалтерия: Подтвердждено ✅"
    
                response = microservices.sendtotelegramchannel(bot_token=BOT_TOKEN,chat_id=CHANNEL_id,message_text=message)
        return data
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="not found exceptnion "
        )






@app.get('/get/done/order/list',response_model=Page[schemas.GetCategoryAsPaginated])
async def get_order_done_list(db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):

    order = crud.get_done_order_list(db=db,role = request_user.role)
    if not order:
        return {'message':'you cannot get this data because you arenot confirmed', 'success':False}
    #order = [{'id':i.id,'status':i.status,'category':i.category.name , 'purchaser':i.purchaser, 'product':i.product,'seller':i.seller,'delivery_time':i.delivery_time,'price':i.price,'payer':i.payer,'urgent':i.urgent,'description':i.description,'payment_type':i.payment_type,'image_url':i.image_url} for i in order ]

    return paginate(order)



    
##############################authorization new







#@app.post('/signup', summary="Create new user",)
#async def create_user(form_data: schemas.UserCreate,db:Session=Depends(get_db)):
#    # querying database to check if user already exist
#    user = crud.get_user(db,username=form_data.username)
#    if user is not None:
#            raise HTTPException(
#            status_code=status.HTTP_400_BAD_REQUEST,
#            detail="User with this email already exist"
#        )
#    user = {
#        'username': form_data.username,
#        'hashed_password': microservices.get_hashed_password(form_data.password),
#    }
#    crud.create_user(db,form_data)
#       # saving user to database
#    return user




@app.post('/login/2', summary="Create access and refresh tokens for user")
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db:Session=Depends(get_db)):
    user = crud.get_user(db,form_data.username)
    if user is None or user.role not in ['musa','shakhzod','begzod','fin','accountant','purchasing','superadmin','nakladnoy']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user.hashed_password
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    return {
        "access_token": create_access_token2(user.username),
        "refresh_token": create_refresh_token2(user.username),
    }



@app.get('/me', summary='Get details of currently logged in user',response_model_exclude=['id'])
async def get_me(user: schemas.TokenRequest = Depends(get_current_user)):
    return schemas.User(username=user.username,id=user.id,role=user.role,full_name=user.full_name)





#########################################bot apis


@app.post('/tel/me')
async def get_me_telid(id:schemas.GetTelId,db:Session=Depends(get_db)):
    user = crud.get_user_with_telid(db,id)
    
    if not user:
        return {'message':'user_doesnot exist','success':False}
    
    return  dict(schemas.User(id=user.id,username=user.username,role=user.role,full_name=user.full_name))


@app.post('/update/order/status/from/telegram')
async def updatestatuswithtel(form_data:schemas.TelAcceptReject,db:Session=Depends(get_db)):
    user = crud.get_user_with_telid(db,form_data)
    if user and user.role not in ['musa','shakhzod','begzod','fin']:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="you cannot perform this action because you may not be owner of this order"
        )
    data = crud.order_accept_db(db,order_id=form_data.order_id,status=form_data.status,role=user.role)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="you cannot perform this action because you may not be owner of this order"
        )
    datetime_object = datetime.strptime(data.delivery_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    year = datetime_object.strftime("%Y")
    month = datetime_object.strftime("%m")
    day = datetime_object.strftime("%d")
    hours = datetime_object.strftime("%H")
    minutes = datetime_object.strftime("%M")
    dateandtime = f"{year}-{month}-{day}, {hours}:{minutes}"
    if data.status not in['denied','paid']:
        user = crud.get_one_user_with_role(db,data.status)
        if data.status=='accountant':
            message= f"Заявка № {data.id}\n🔘Тип: {data.category.name}\n🙍‍♂Заказчик: {data.purchaser}\n📦"
            microservices.sendtotelegramchannel(bot_token=BOT_TOKEN,chat_id=user.telegram_id,message_text=message)
        else:
            message= f"Заявка № {data.id}\n🔘Тип: {data.category.name}\n🙍‍♂Заказчик: {data.purchaser}\n📦Товар: {data.product}\n👨‍💼Поставщик: {data.seller}\n🕘Срок: {dateandtime}\n💰Стоимость: {data.price} UZS\n💲Тип оплаты: {data.payment_type}\n💳Плательщик: {data.payer}\nℹ️Описание: {data.description}"

            response = microservices.sendtotelegram(bot_token=BOT_TOKEN,chat_id=user.telegram_id,message_text=message)

    if data.status == 'denied':
        message= f"Заявка № {data.id}\n🔘Тип: {data.category.name}\n🙍‍♂Заказчик: {data.purchaser}\n📦Товар: {data.product}\n👨‍💼Поставщик: {data.seller}\n🕘Срок: {dateandtime}\n💰Стоимость: {data.price} UZS\n💲Тип оплаты: {data.payment_type}\n💳Плательщик: {data.payer}\nℹ️Описание: {data.description}\n📝 Комментарии: \n\n{admindict[user.role]} ❌"
    
        response = microservices.sendtotelegramchannel(bot_token=BOT_TOKEN,chat_id=CHANNEL_id,message_text=message)
    return data
add_pagination(app)
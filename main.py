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

from database import engine,SessionLocal
from microservices import create_access_token,verify_password
from typing import Optional,Annotated
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm

models.Base.metadata.create_all(bind=engine)
import bcrypt
app = FastAPI()
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = 'thisistokenforusersecretauth'   # should be kept secret
JWT_REFRESH_SECRET_KEY =  'thisistokenforusersecretrefresh'

origins = ["*"]


reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login/2",
    scheme_name="JWT"
)


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
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)




@app.post("/login")
async def generate_token(form_data: schemas.TokenRequest, db: Session = Depends(get_db)):
    user = crud.get_user(db, username=form_data.username)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    elif not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

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
    try:
        data = crud.create_order(db,order=form)

    except:
        return {'message':'category id is not valid so change it','success':False}
    return data

@app.post('/image/upload',response_model_include=['id'])
async def create_order(image:UploadFile,db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    with open(f"uploads/{image.filename}", 'wb') as f:
        shutil.copyfileobj(image.file,f)
    
    return crud.create_image(db,image_url=f"uploads/{image.filename}")



@app.put('/update/user/role')
async def update_user_role(form:schemas.UpdateUserRole,db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    try:
        data = crud.update_role(db=db,user_id=form.user_id,role=form.role)
        
    except:
        return {'message':'couldnot found user or the user with this role already exist'}
    if not data:
        return {'message':'couldnot found user or the user with this role already existwer'}
    return data



@app.get('/get/user/list/with/role',response_model_exclude=['id',],)
async def get_user_list(db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    data  = crud.get_user_list(db=db)
    return data


@app.get('/get/order/list')
async def get_order_list(db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):

    data = crud.get_order_list(db=db,role = request_user.role)
    if not data:
        return {'message':'you cannot get this data because you arenot confirmed', 'success':False}
    #print(schemas.Create_Order(data))
    return data



@app.get('/get/list/of/roles')
async def get_roles(request_user: schemas.User = Depends(get_current_user)):
    list_of_roles = ['musa','shakhzod','begzod','fin','accountant','unconfirmed','purchasing']
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
    return order


@app.put('/order/accept/reject/{order_id}/{status}')
async def order_accept_reject(order_id:int,status:str,db:Session=Depends(get_db),request_user: schemas.User = Depends(get_current_user)):
    if request_user.role in ['unconfirmed','purshasing']:
        return {'message':'you cannot perform this action','success':False}
    order_accept = crud.order_accept_db(db,order_id=order_id,status=status,role=request_user.role)
    if not order_accept:
        return {'message':'you cannot vote for this order. reason you may not be owner or accaptable status are accepted,denied','success':True}
    return order_accept
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
    if user is None:
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
    return schemas.User(username=user.username,id=user.id,role=user.role)
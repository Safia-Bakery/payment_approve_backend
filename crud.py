from sqlalchemy.orm import Session
import models
import schemas
from sqlalchemy import or_,and_
import bcrypt

def hash_password(password):
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed_password.decode("utf-8")

def create_user(db: Session, user: schemas.UserCreate,username):
    hashed_password = hash_password(user.password)
    db_user = models.User(username=username, hashed_password=hashed_password,full_name=user.full_name,telegram_id = int(user.telegram_id))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_category(db:Session,name:schemas.CategoryCreate):
    db_category = models.Category(name=name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category




def get_category_list(db:Session,):
    return db.query(models.Category).all()



def create_order(db:Session,order:schemas.Create_Order):

    db_order = models.Order(category_id=order.category_id,
                            purchaser=order.purchaser,
                            product=order.product,
                            seller=order.seller,
                            delivery_time=order.delivery_time,
                            price=order.price,
                            payer = order.payer,
                            payment_type=order.payment_type,
                            description=order.description,
                            urgent=order.urgent,
                            image_id=order.image_id,
                            user_id=order.user_id
                            )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order




def create_image(db:Session,image_url):
    db_image = models.ImageUpload(image_url=image_url)
    db.add(db_image)
    db.commit()
    db.refresh(db_image)
    return db_image


def update_role(db:Session,user_id,role):
    db_user_update = db.query(models.User).filter(models.User.id==user_id).first()
    if db_user_update:
        db_user_update.role = role
        db.commit()
        db.refresh(db_user_update)
        return db_user_update



    

def get_user_list(db:Session):
    return db.query(models.User).all()


def get_order_list(db:Session,role,user_id):
    if role in ['musa','shakhzod','begzod','fin']:
        return db.query(models.Order).filter(models.Order.status==role).order_by(models.Order.time_created.desc()).all()
    elif role in ['purchasing','superadmin']:
        return db.query(models.Order).order_by(models.Order.time_created.desc()).all()
    elif role == 'accountant':
        return db.query(models.Order).filter(or_(models.Order.user_id==user_id,models.Order.status=='accountant')).all()
    elif role == 'nakladnoy':
        return db.query(models.Order).filter(and_(models.Order.user_id==user_id,models.Order.status=='paid')).all()
    else: 
        return None
    

def get_done_order_list(db:Session,role):
    if role in ['musa','shakhzod','begzod','fin','accountant','purchasing','superadmin']:
        return db.query(models.Order).filter(or_(models.Order.status=='paid',models.Order.status=='denied')).order_by(models.Order.time_created.desc()).all()
    else: 
        return None


def get_user_with_idcr(db:Session,user_id):
    return db.query(models.User).filter(models.User.id==user_id).first()

def get_order_with_id(db:Session,order_id):
    return db.query(models.Order).filter(models.Order.id==order_id).first()

def order_accept_db(db:Session,order_id,role,status):
    db_order_accept = db.query(models.Order).filter(models.Order.id==order_id).first()
    if db_order_accept and role == db_order_accept.status:
        if status =='accepted' and db_order_accept.status=='musa' and db_order_accept.category.name =='Фабрика':
            db_order_accept.status = 'shakhzod'
        elif status =='accepted' and db_order_accept.status=='musa' and db_order_accept.category.name =='Розница':
            db_order_accept.status = 'begzod'
        elif status =='accepted' and db_order_accept.status=='begzod':
            db_order_accept.status = 'fin'
        elif status =='accepted' and db_order_accept.status=='shakhzod':
            db_order_accept.status = 'fin'
        elif status =='accepted' and db_order_accept.status=='fin':
            db_order_accept.status = 'accountant'
        elif status =='denied':
            db_order_accept.status ='denied'
        else:
            return False
    else: 
        return False
    db.commit()
    db.refresh(db_order_accept)
    return db_order_accept


def get_user_with_telid(db:Session,tel):
    db_telegram = db.query(models.User).filter(models.User.telegram_id==tel.telid).first()
    return db_telegram
    


def get_one_user_with_role(db:Session,role):
    user_with_role = db.query(models.User).filter(models.User.role==role).first()
    return user_with_role




def add_paid_amaunt_order(db:Session,form_data:schemas.OrderAddPaid):
    query = db.query(models.Order).filter(models.Order.id==form_data.order_id).first()
    if form_data.paid_amount is not None:
        if query.amount_paid:
            overall = form_data.paid_amount+query.amount_paid
            if overall>=query.price:
                query.status='paid'
            
            query.amount_paid = overall
        else:
            query.amount_paid=form_data.paid_amount
    if form_data.nakladnoy is not None:
        query.nakladnoy = form_data.nakladnoy
    db.commit()
    db.refresh(query)
    return query


def get_user_nakladnoy(db:Session):
    query = db.query(models.User).filter(or_(models.User.role=='accountant',models.User.role=='unconfirmed',models.User.role=='nakladnoy')).all()
    return query

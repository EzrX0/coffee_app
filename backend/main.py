from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
import os
import models
import schemas
import stripe
from auth import get_current_user, get_password_hash, create_access_token
from database import SessionLocal, engine



stripe.api_key = os.getenv("STRIPE_API_KEY")

# Drop tables so we can recreate them with the new schema (DANGEROUS IN PROD, OK FOR DEV)
# models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Coffee App API")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/signup", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    from auth import verify_password
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    if db.query(models.Coffee).count() == 0:
        dummy_data = [
            # Cappuccino
            models.Coffee(
                name='Cappuccino',
                subtitle='with Chocolate',
                price=4.53,
                rating=4.8,
                imageUrl='https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=400',
            ),
            models.Coffee(
                name='Cappuccino',
                subtitle='with Oat Milk',
                price=3.90,
                rating=4.9,
                imageUrl='https://images.unsplash.com/photo-1534778101976-62847782c213?w=400',
            ),
            models.Coffee(
                name='Cappuccino',
                subtitle='with Vanilla',
                price=4.55,
                rating=4.5,
                imageUrl='https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?w=400',
            ),
            models.Coffee(
                name='Cappuccino',
                subtitle='with Caramel',
                price=5.20,
                rating=4.0,
                imageUrl='https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400',
            ),
            # Machiato
            models.Coffee(
                name='Machiato',
                subtitle='Espresso Machiato',
                price=3.50,
                rating=4.7,
                imageUrl='https://images.unsplash.com/photo-1485808191679-5f86510681a2?w=400',
            ),
            models.Coffee(
                name='Machiato',
                subtitle='Caramel Machiato',
                price=4.80,
                rating=4.6,
                imageUrl='https://images.unsplash.com/photo-1558857563-b371033873b8?w=400',
            ),
            models.Coffee(
                name='Machiato',
                subtitle='Latte Machiato',
                price=4.20,
                rating=4.4,
                imageUrl='https://images.unsplash.com/photo-1611564494260-6f21b80af7ea?w=400',
            ),
            models.Coffee(
                name='Machiato',
                subtitle='Hazelnut Machiato',
                price=4.90,
                rating=4.3,
                imageUrl='https://images.unsplash.com/photo-1442512595331-e89e73853f31?w=400',
            ),
            # Latte
            models.Coffee(
                name='Latte',
                subtitle='Classic Latte',
                price=4.00,
                rating=4.8,
                imageUrl='https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?w=400',
            ),
            models.Coffee(
                name='Latte',
                subtitle='Vanilla Latte',
                price=4.50,
                rating=4.7,
                imageUrl='https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400',
            ),
            models.Coffee(
                name='Latte',
                subtitle='Caramel Latte',
                price=4.70,
                rating=4.5,
                imageUrl='https://images.unsplash.com/photo-1561882468-9110e03e0f78?w=400',
            ),
            models.Coffee(
                name='Latte',
                subtitle='Matcha Latte',
                price=5.00,
                rating=4.9,
                imageUrl='https://images.unsplash.com/photo-1536256263959-770b48d82b0a?w=400',
            ),
            # Americano
            models.Coffee(
                name='Americano',
                subtitle='Classic Americano',
                price=3.00,
                rating=4.6,
                imageUrl='https://images.unsplash.com/photo-1551030173-122aabc4489c?w=400',
            ),
            models.Coffee(
                name='Americano',
                subtitle='Iced Americano',
                price=3.50,
                rating=4.8,
                imageUrl='https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=400',
            ),
            models.Coffee(
                name='Americano',
                subtitle='White Americano',
                price=3.80,
                rating=4.3,
                imageUrl='https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400',
            ),
            models.Coffee(
                name='Americano',
                subtitle='Double Shot',
                price=4.00,
                rating=4.5,
                imageUrl='https://images.unsplash.com/photo-1497515114889-60a4f2dc0e75?w=400',
            ),
        ]
        db.add_all(dummy_data)
        db.commit()
    db.close()

@app.get("/api/coffees", response_model=list[schemas.Coffee])
def read_coffees(
    skip: int = 0, 
    limit: int = 100, 
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Coffee)
    if category and category != 'All':
        query = query.filter(models.Coffee.name.ilike(f"%{category}%"))
    if search:
        query = query.filter(models.Coffee.name.ilike(f"%{search}%") | models.Coffee.subtitle.ilike(f"%{search}%"))
        
    coffees = query.offset(skip).limit(limit).all()
    return coffees

@app.post("/api/coffees", response_model=schemas.Coffee)
def create_coffee(coffee: schemas.CoffeeCreate, db: Session = Depends(get_db)):
    db_coffee = models.Coffee(**coffee.model_dump())
    db.add(db_coffee)
    db.commit()
    db.refresh(db_coffee)
    return db_coffee

@app.get("/api/favorites", response_model=list[schemas.Favorite])
def read_favorites(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Favorite).filter(models.Favorite.user_id == current_user.id).all()

@app.post("/api/favorites", response_model=schemas.Favorite)
def add_favorite(favorite: schemas.FavoriteBase, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(models.Favorite).filter(
        models.Favorite.coffee_id == favorite.coffee_id,
        models.Favorite.user_id == current_user.id
    ).first()
    if existing:
        return existing
    db_favorite = models.Favorite(coffee_id=favorite.coffee_id, user_id=current_user.id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

@app.delete("/api/favorites/{coffee_id}")
def remove_favorite(coffee_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_favorite = db.query(models.Favorite).filter(
        models.Favorite.coffee_id == coffee_id,
        models.Favorite.user_id == current_user.id
    ).first()
    if db_favorite:
        db.delete(db_favorite)
        db.commit()
    return {"status": "success"}

@app.get("/api/cart", response_model=list[schemas.CartItem])
def read_cart(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()

@app.post("/api/cart", response_model=schemas.CartItem)
def add_to_cart(cart_item: schemas.CartItemBase, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    existing = db.query(models.CartItem).filter(
        models.CartItem.coffee_id == cart_item.coffee_id,
        models.CartItem.size == cart_item.size,
        models.CartItem.user_id == current_user.id
    ).first()
    
    if existing:
        existing.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing)
        return existing
        
    db_item = models.CartItem(**cart_item.model_dump(), user_id=current_user.id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/api/cart/{cart_item_id}")
def remove_from_cart(cart_item_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.CartItem).filter(
        models.CartItem.id == cart_item_id,
        models.CartItem.user_id == current_user.id
    ).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return {"status": "success"}

@app.post("/api/create-payment-intent")
def create_payment_intent(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total_price = sum(item.coffee.price * item.quantity for item in cart_items)
    # Stripe expects amount in cents
    amount_cents = int(round(total_price * 100))
    
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency='usd',
            metadata={'user_id': str(current_user.id)},
        )
        return {"client_secret": intent.client_secret, "amount": total_price}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/checkout", response_model=schemas.Order)
def checkout(payload: Optional[schemas.CheckoutRequest] = None, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    cart_items = db.query(models.CartItem).filter(models.CartItem.user_id == current_user.id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    total_price = sum(item.coffee.price * item.quantity for item in cart_items)
    payment_intent_id = payload.payment_intent_id if payload else None
    
    db_order = models.Order(user_id=current_user.id, total_price=total_price, payment_intent_id=payment_intent_id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    for item in cart_items:
        db_order_item = models.OrderItem(
            order_id=db_order.id,
            coffee_id=item.coffee_id,
            size=item.size,
            quantity=item.quantity,
            price=item.coffee.price
        )
        db.add(db_order_item)
        db.delete(item) # remove from cart
        
    db.commit()
    db.refresh(db_order)
    return db_order

@app.get("/api/orders", response_model=list[schemas.Order])
def get_orders(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Order).filter(models.Order.user_id == current_user.id).order_by(models.Order.created_at.desc()).all()

@app.get("/api/me", response_model=schemas.User)
def get_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.put("/api/password")
def update_password(payload: schemas.PasswordUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    from auth import verify_password, get_password_hash
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    current_user.hashed_password = get_password_hash(payload.new_password)
    db.commit()
    return {"status": "success"}

from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
import os
import models
import schemas
import stripe
from auth import get_current_user, get_password_hash, create_access_token, create_refresh_token, verify_refresh_token
from database import SessionLocal, engine, get_db



stripe.api_key = os.getenv("STRIPE_API_KEY")

# Drop tables so we can recreate them with the new schema (DANGEROUS IN PROD, OK FOR DEV)
# models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed the database
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
                description='A rich cappuccino topped with velvety chocolate shavings and a dusting of cocoa powder. The perfect balance of espresso intensity and sweet indulgence.',
            ),
            models.Coffee(
                name='Cappuccino',
                subtitle='with Oat Milk',
                price=3.90,
                rating=4.9,
                imageUrl='https://images.unsplash.com/photo-1534778101976-62847782c213?w=400',
                description='A creamy, plant-based cappuccino made with barista-grade oat milk. Naturally sweet with a silky-smooth texture that froths beautifully.',
            ),
            models.Coffee(
                name='Cappuccino',
                subtitle='with Vanilla',
                price=4.55,
                rating=4.5,
                imageUrl='https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?w=400',
                description='Classic cappuccino infused with Madagascar vanilla bean extract. A fragrant, comforting twist on the Italian original.',
            ),
            models.Coffee(
                name='Cappuccino',
                subtitle='with Caramel',
                price=5.20,
                rating=4.0,
                imageUrl='https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400',
                description='A luscious cappuccino drizzled with house-made salted caramel. Bold espresso meets buttery sweetness in every sip.',
            ),
            # Machiato
            models.Coffee(
                name='Machiato',
                subtitle='Espresso Machiato',
                price=3.50,
                rating=4.7,
                imageUrl='https://images.unsplash.com/photo-1485808191679-5f86510681a2?w=400',
                description='A traditional espresso "stained" with just a dollop of steamed milk foam. Intense, bold, and perfect for purists.',
            ),
            models.Coffee(
                name='Machiato',
                subtitle='Caramel Machiato',
                price=4.80,
                rating=4.6,
                imageUrl='https://images.unsplash.com/photo-1558857563-b371033873b8?w=400',
                description='Layers of vanilla-infused steamed milk, rich espresso, and a crosshatch of caramel sauce. A sweet and sophisticated classic.',
            ),
            models.Coffee(
                name='Machiato',
                subtitle='Latte Machiato',
                price=4.20,
                rating=4.4,
                imageUrl='https://images.unsplash.com/photo-1611564494260-6f21b80af7ea?w=400',
                description='Steamed milk "stained" with a shot of espresso, creating beautiful layers. Milder and creamier than a traditional machiato.',
            ),
            models.Coffee(
                name='Machiato',
                subtitle='Hazelnut Machiato',
                price=4.90,
                rating=4.3,
                imageUrl='https://images.unsplash.com/photo-1442512595331-e89e73853f31?w=400',
                description='A nutty twist on the classic machiato with roasted hazelnut syrup. Warm, toasty flavors complement the espresso perfectly.',
            ),
            # Latte
            models.Coffee(
                name='Latte',
                subtitle='Classic Latte',
                price=4.00,
                rating=4.8,
                imageUrl='https://images.unsplash.com/photo-1570968915860-54d5c301fa9f?w=400',
                description='The timeless café latte — a perfect ratio of espresso and steamed milk topped with a thin layer of microfoam. Smooth, mellow, and endlessly satisfying.',
            ),
            models.Coffee(
                name='Latte',
                subtitle='Vanilla Latte',
                price=4.50,
                rating=4.7,
                imageUrl='https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400',
                description='Our classic latte enhanced with premium vanilla syrup. A crowd favorite that balances coffee character with gentle sweetness.',
            ),
            models.Coffee(
                name='Latte',
                subtitle='Caramel Latte',
                price=4.70,
                rating=4.5,
                imageUrl='https://images.unsplash.com/photo-1561882468-9110e03e0f78?w=400',
                description='A velvety latte swirled with rich caramel sauce and topped with whipped cream. Dessert in a cup.',
            ),
            models.Coffee(
                name='Latte',
                subtitle='Matcha Latte',
                price=5.00,
                rating=4.9,
                imageUrl='https://images.unsplash.com/photo-1536256263959-770b48d82b0a?w=400',
                description='Ceremonial-grade Japanese matcha whisked with steamed milk. Earthy, vibrant, and packed with natural antioxidants.',
            ),
            # Americano
            models.Coffee(
                name='Americano',
                subtitle='Classic Americano',
                price=3.00,
                rating=4.6,
                imageUrl='https://images.unsplash.com/photo-1551030173-122aabc4489c?w=400',
                description='Double espresso diluted with hot water to create a clean, bold coffee. All the flavor of espresso with a lighter body.',
            ),
            models.Coffee(
                name='Americano',
                subtitle='Iced Americano',
                price=3.50,
                rating=4.8,
                imageUrl='https://images.unsplash.com/photo-1517701604599-bb29b565090c?w=400',
                description='Chilled double espresso poured over ice and cold water. Crisp, refreshing, and perfect for warm days.',
            ),
            models.Coffee(
                name='Americano',
                subtitle='White Americano',
                price=3.80,
                rating=4.3,
                imageUrl='https://images.unsplash.com/photo-1509042239860-f550ce710b93?w=400',
                description='An Americano finished with a splash of steamed milk. A smoother, softer take on the black coffee classic.',
            ),
            models.Coffee(
                name='Americano',
                subtitle='Double Shot',
                price=4.00,
                rating=4.5,
                imageUrl='https://images.unsplash.com/photo-1497515114889-60a4f2dc0e75?w=400',
                description='An extra-strength Americano made with a triple shot of espresso. Maximum caffeine, maximum flavor, zero compromise.',
            ),
        ]
        db.add_all(dummy_data)
        db.commit()
    db.close()
    yield
    # Shutdown: nothing needed


limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Coffee App API", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/signup", response_model=schemas.User)
@limiter.limit("5/minute")
def signup(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
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
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    from auth import verify_password
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    refresh_token = create_refresh_token(user_id=user.id, db=db)
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}

@app.post("/api/refresh", response_model=schemas.Token)
def refresh(payload: schemas.RefreshTokenRequest, db: Session = Depends(get_db)):
    result = verify_refresh_token(payload.refresh_token, db)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    user, db_token = result
    
    # Issue new access token
    access_token = create_access_token(data={"sub": user.username})
    # Issue new refresh token
    new_refresh_token = create_refresh_token(user_id=user.id, db=db)
    
    # Delete old refresh token
    db.delete(db_token)
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": new_refresh_token}

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

@app.put("/api/cart/{cart_item_id}", response_model=schemas.CartItem)
def update_cart_item(cart_item_id: int, item_update: schemas.CartItemUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_item = db.query(models.CartItem).filter(
        models.CartItem.id == cart_item_id,
        models.CartItem.user_id == current_user.id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db_item.quantity = item_update.quantity
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
    
    total_price = sum(
        (item.coffee.price + (0.50 if item.size == 'M' else 1.00 if item.size == 'L' else 0.0)) * item.quantity 
        for item in cart_items
    )
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
    
    total_price = sum(
        (item.coffee.price + (0.50 if item.size == 'M' else 1.00 if item.size == 'L' else 0.0)) * item.quantity 
        for item in cart_items
    )
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
            price=item.coffee.price + (0.50 if item.size == 'M' else 1.00 if item.size == 'L' else 0.0)
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

@app.get("/api/notifications", response_model=list[schemas.Notification])
def get_notifications(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Create some dummy notifications if the user has none (for demonstration purposes)
    count = db.query(models.Notification).filter(models.Notification.user_id == current_user.id).count()
    if count == 0:
        dummy_notifications = [
            models.Notification(user_id=current_user.id, title='Welcome!', description='Thanks for joining the Coffee App.', type='status'),
            models.Notification(user_id=current_user.id, title='Special Promo', description='Get 20% off all Lattes today! Use code LATTE20 at checkout.', type='offer'),
        ]
        db.add_all(dummy_notifications)
        db.commit()

    return db.query(models.Notification).filter(models.Notification.user_id == current_user.id).order_by(models.Notification.created_at.desc()).all()

@app.put("/api/notifications/{notification_id}/read", response_model=schemas.Notification)
def mark_notification_read(notification_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notification.is_read = 1
    db.commit()
    db.refresh(notification)
    return notification

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from sqlalchemy.orm import Session
import models
import schemas
from database import SessionLocal, engine

# Create the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Coffee App API")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.on_event("startup")
def startup_event():
    # Pre-populate database with dummy data if it's empty
    db = SessionLocal()
    if db.query(models.Coffee).count() == 0:
        dummy_data = [
            models.Coffee(
                name='Cappucino',
                subtitle='with Chocolate',
                price=4.53,
                rating=4.8,
                imageUrl='https://images.unsplash.com/photo-1572442388796-11668a67e53d?w=400',
            ),
            models.Coffee(
                name='Cappucino',
                subtitle='with Oat Milk',
                price=3.90,
                rating=4.9,
                imageUrl='https://images.unsplash.com/photo-1534778101976-62847782c213?w=400',
            ),
            models.Coffee(
                name='Cappucino',
                subtitle='with Chocolate',
                price=4.55,
                rating=4.5,
                imageUrl='https://images.unsplash.com/photo-1517701550927-30cf4ba1dba5?w=400',
            ),
            models.Coffee(
                name='Cappucino',
                subtitle='with Oat Milk',
                price=5.20,
                rating=4.0,
                imageUrl='https://images.unsplash.com/photo-1461023058943-07fcbe16d735?w=400',
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
def read_favorites(db: Session = Depends(get_db)):
    return db.query(models.Favorite).all()

@app.post("/api/favorites", response_model=schemas.Favorite)
def add_favorite(favorite: schemas.FavoriteBase, db: Session = Depends(get_db)):
    existing = db.query(models.Favorite).filter(models.Favorite.coffee_id == favorite.coffee_id).first()
    if existing:
        return existing
    db_favorite = models.Favorite(coffee_id=favorite.coffee_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

@app.delete("/api/favorites/{coffee_id}")
def remove_favorite(coffee_id: int, db: Session = Depends(get_db)):
    db_favorite = db.query(models.Favorite).filter(models.Favorite.coffee_id == coffee_id).first()
    if db_favorite:
        db.delete(db_favorite)
        db.commit()
    return {"status": "success"}

@app.get("/api/cart", response_model=list[schemas.CartItem])
def read_cart(db: Session = Depends(get_db)):
    return db.query(models.CartItem).all()

@app.post("/api/cart", response_model=schemas.CartItem)
def add_to_cart(cart_item: schemas.CartItemBase, db: Session = Depends(get_db)):
    existing = db.query(models.CartItem).filter(
        models.CartItem.coffee_id == cart_item.coffee_id,
        models.CartItem.size == cart_item.size
    ).first()
    
    if existing:
        existing.quantity += cart_item.quantity
        db.commit()
        db.refresh(existing)
        return existing
        
    db_item = models.CartItem(**cart_item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.delete("/api/cart/{cart_item_id}")
def remove_from_cart(cart_item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.CartItem).filter(models.CartItem.id == cart_item_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
    return {"status": "success"}

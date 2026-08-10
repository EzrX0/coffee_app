from pydantic import BaseModel
from typing import List, Optional

class CoffeeBase(BaseModel):
    name: str
    subtitle: str
    price: float
    rating: float
    imageUrl: str

class CoffeeCreate(CoffeeBase):
    pass

class Coffee(CoffeeBase):
    id: int

    class Config:
        from_attributes = True

class FavoriteBase(BaseModel):
    coffee_id: int

class Favorite(FavoriteBase):
    id: int
    coffee: Coffee

    class Config:
        from_attributes = True

class CartItemBase(BaseModel):
    coffee_id: int
    size: str
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int
    coffee: Coffee

    class Config:
        from_attributes = True

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

class CoffeeBase(BaseModel):
    name: str
    subtitle: str
    price: float
    rating: float
    imageUrl: str
    description: Optional[str] = None

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

class CartItemUpdate(BaseModel):
    quantity: int

class CartItem(CartItemBase):
    id: int
    coffee: Coffee

    class Config:
        from_attributes = True

class CheckoutRequest(BaseModel):
    payment_intent_id: Optional[str] = None

class OrderItemBase(BaseModel):
    coffee_id: int
    size: str
    quantity: int
    price: float

class OrderItem(OrderItemBase):
    id: int
    coffee: Coffee

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    total_price: float
    payment_intent_id: Optional[str] = None

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    user_id: int
    created_at: datetime
    status: str
    items: List[OrderItem] = []

    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    title: str
    description: str
    type: str

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: int
    created_at: datetime

    class Config:
        from_attributes = True

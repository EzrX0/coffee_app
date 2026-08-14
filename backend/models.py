from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    favorites = relationship("Favorite", back_populates="user", cascade="all, delete-orphan")
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

class Coffee(Base):
    __tablename__ = "coffees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    subtitle = Column(String)
    price = Column(Float)
    rating = Column(Float)
    imageUrl = Column(String)

    favorites = relationship("Favorite", back_populates="coffee")
    cart_items = relationship("CartItem", back_populates="coffee")

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    coffee_id = Column(Integer, ForeignKey("coffees.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    coffee = relationship("Coffee", back_populates="favorites")
    user = relationship("User", back_populates="favorites")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    coffee_id = Column(Integer, ForeignKey("coffees.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    size = Column(String)
    quantity = Column(Integer, default=1)

    coffee = relationship("Coffee", back_populates="cart_items")
    user = relationship("User", back_populates="cart_items")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Float)
    payment_intent_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    coffee_id = Column(Integer, ForeignKey("coffees.id"))
    size = Column(String)
    quantity = Column(Integer)
    price = Column(Float) # price at the time of purchase

    order = relationship("Order", back_populates="items")
    coffee = relationship("Coffee")

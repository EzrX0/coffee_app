from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

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
    
    coffee = relationship("Coffee", back_populates="favorites")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    coffee_id = Column(Integer, ForeignKey("coffees.id"))
    size = Column(String)
    quantity = Column(Integer, default=1)

    coffee = relationship("Coffee", back_populates="cart_items")

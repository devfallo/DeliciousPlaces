from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    source_type = Column(String(30), nullable=False, default="Hybrid")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_low_sodium_certified = Column(Boolean, default=False)
    tv_feature_info = Column(JSON, nullable=True)

    menus = relationship("Menu", back_populates="restaurant", cascade="all, delete-orphan")


class Menu(Base):
    __tablename__ = "menus"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    price = Column(Integer, nullable=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)

    restaurant = relationship("Restaurant", back_populates="menus")
    taste_score = relationship(
        "MenuTasteScore",
        uselist=False,
        back_populates="menu",
        cascade="all, delete-orphan",
    )


class MenuTasteScore(Base):
    __tablename__ = "menu_taste_scores"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False, unique=True)
    spiciness_level = Column(Float, nullable=False)
    saltiness_level = Column(Float, nullable=False)
    sweetness_level = Column(Float, nullable=False)
    review_count = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, nullable=False, default=datetime.utcnow)

    menu = relationship("Menu", back_populates="taste_score")


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_key = Column(String(100), nullable=False, unique=True, index=True)
    spicy_tolerance = Column(Integer, nullable=False)
    sodium_sensitivity = Column(Boolean, nullable=False, default=False)
    disliked_ingredients = Column(JSON, nullable=False, default=list)


class ReviewSignal(Base):
    __tablename__ = "review_signals"

    id = Column(Integer, primary_key=True, index=True)
    menu_id = Column(Integer, ForeignKey("menus.id"), nullable=False, index=True)
    source_type = Column(String(30), nullable=False)  # tv, receipt_verified, blog, general
    text = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class MenuTasteScoreBase(BaseModel):
    spiciness_level: float = Field(ge=1.0, le=5.0)
    saltiness_level: float = Field(ge=1.0, le=5.0)
    sweetness_level: float = Field(ge=1.0, le=5.0)
    review_count: int = Field(default=0, ge=0)


class MenuTasteScoreRead(MenuTasteScoreBase):
    menu_id: int
    last_updated: datetime

    class Config:
        from_attributes = True


class MenuCreate(BaseModel):
    name: str
    price: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class MenuRead(BaseModel):
    id: int
    name: str
    price: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    taste_score: Optional[MenuTasteScoreRead] = None

    class Config:
        from_attributes = True


class RestaurantCreate(BaseModel):
    name: str
    source_type: str = "Hybrid"
    latitude: float
    longitude: float
    is_low_sodium_certified: bool = False
    tv_feature_info: Optional[dict] = None
    menus: List[MenuCreate] = []


class RestaurantRead(BaseModel):
    id: int
    name: str
    source_type: str
    latitude: float
    longitude: float
    is_low_sodium_certified: bool
    tv_feature_info: Optional[dict] = None
    menus: List[MenuRead] = []

    class Config:
        from_attributes = True


class UserPreferenceUpsert(BaseModel):
    user_key: str
    spicy_tolerance: int = Field(ge=1, le=5)
    sodium_sensitivity: bool
    disliked_ingredients: List[str] = []


class UserPreferenceRead(UserPreferenceUpsert):
    id: int

    class Config:
        from_attributes = True


class ReviewSignalCreate(BaseModel):
    source_type: str = Field(pattern="^(tv|receipt_verified|blog|general)$")
    text: str
    created_at: Optional[datetime] = None


class RecommendationQuery(BaseModel):
    user_key: Optional[str] = None
    min_spiciness: float = Field(default=1.0, ge=1.0, le=5.0)
    max_spiciness: float = Field(default=5.0, ge=1.0, le=5.0)
    low_sodium_only: bool = False


class RecommendationItem(BaseModel):
    restaurant_id: int
    restaurant_name: str
    menu_id: int
    menu_name: str
    spiciness_level: float
    saltiness_level: float
    ai_comment: str


class RecommendationResponse(BaseModel):
    items: List[RecommendationItem]

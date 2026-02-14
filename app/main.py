from datetime import datetime

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database import Base, engine, get_db
from app import models, schemas
from app.taste_engine import aggregate_menu_scores

Base.metadata.create_all(bind=engine)

app = FastAPI(title="DeliciousPlaces API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/restaurants", response_model=schemas.RestaurantRead)
def create_restaurant(payload: schemas.RestaurantCreate, db: Session = Depends(get_db)):
    restaurant = models.Restaurant(
        name=payload.name,
        source_type=payload.source_type,
        latitude=payload.latitude,
        longitude=payload.longitude,
        is_low_sodium_certified=payload.is_low_sodium_certified,
        tv_feature_info=payload.tv_feature_info,
    )
    db.add(restaurant)
    db.flush()

    for menu_payload in payload.menus:
        db.add(
            models.Menu(
                restaurant_id=restaurant.id,
                name=menu_payload.name,
                price=menu_payload.price,
                description=menu_payload.description,
                image_url=menu_payload.image_url,
            )
        )

    db.commit()
    db.refresh(restaurant)
    return restaurant


@app.get("/restaurants", response_model=list[schemas.RestaurantRead])
def list_restaurants(db: Session = Depends(get_db)):
    return db.query(models.Restaurant).options(joinedload(models.Restaurant.menus)).all()


@app.post("/users/preferences", response_model=schemas.UserPreferenceRead)
def upsert_preference(payload: schemas.UserPreferenceUpsert, db: Session = Depends(get_db)):
    preference = (
        db.query(models.UserPreference)
        .filter(models.UserPreference.user_key == payload.user_key)
        .one_or_none()
    )
    if preference is None:
        preference = models.UserPreference(user_key=payload.user_key)
        db.add(preference)

    preference.spicy_tolerance = payload.spicy_tolerance
    preference.sodium_sensitivity = payload.sodium_sensitivity
    preference.disliked_ingredients = payload.disliked_ingredients

    db.commit()
    db.refresh(preference)
    return preference


@app.post("/menus/{menu_id}/signals")
def add_review_signal(menu_id: int, payload: schemas.ReviewSignalCreate, db: Session = Depends(get_db)):
    menu = db.query(models.Menu).filter(models.Menu.id == menu_id).one_or_none()
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")

    signal = models.ReviewSignal(
        menu_id=menu_id,
        source_type=payload.source_type,
        text=payload.text,
        created_at=payload.created_at or datetime.utcnow(),
    )
    db.add(signal)
    db.commit()
    return {"created": True}


@app.post("/menus/{menu_id}/recompute-score", response_model=schemas.MenuTasteScoreRead)
def recompute_menu_score(menu_id: int, db: Session = Depends(get_db)):
    menu = db.query(models.Menu).filter(models.Menu.id == menu_id).one_or_none()
    if menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")

    signals = db.query(models.ReviewSignal).filter(models.ReviewSignal.menu_id == menu_id).all()
    spicy, salty, sweet, count = aggregate_menu_scores(signals)

    score = (
        db.query(models.MenuTasteScore)
        .filter(models.MenuTasteScore.menu_id == menu_id)
        .one_or_none()
    )
    if score is None:
        score = models.MenuTasteScore(menu_id=menu_id, spiciness_level=3, saltiness_level=3, sweetness_level=3)
        db.add(score)

    score.spiciness_level = spicy
    score.saltiness_level = salty
    score.sweetness_level = sweet
    score.review_count = count
    score.last_updated = datetime.utcnow()

    db.commit()
    db.refresh(score)
    return score


@app.post("/recommendations", response_model=schemas.RecommendationResponse)
def get_recommendations(payload: schemas.RecommendationQuery, db: Session = Depends(get_db)):
    low_sodium_only = payload.low_sodium_only
    disliked_ingredients: list[str] = []

    if payload.user_key:
        pref = (
            db.query(models.UserPreference)
            .filter(models.UserPreference.user_key == payload.user_key)
            .one_or_none()
        )
        if pref:
            if pref.sodium_sensitivity:
                low_sodium_only = True
            disliked_ingredients = [
                ingredient.strip().lower()
                for ingredient in (pref.disliked_ingredients or [])
                if ingredient and ingredient.strip()
            ]

    query = (
        db.query(models.Menu, models.Restaurant, models.MenuTasteScore)
        .join(models.Restaurant, models.Menu.restaurant_id == models.Restaurant.id)
        .join(models.MenuTasteScore, models.MenuTasteScore.menu_id == models.Menu.id)
        .filter(models.MenuTasteScore.spiciness_level >= payload.min_spiciness)
        .filter(models.MenuTasteScore.spiciness_level <= payload.max_spiciness)
    )

    if low_sodium_only:
        query = query.filter(
            (models.MenuTasteScore.saltiness_level <= 2.5)
            | (models.Restaurant.is_low_sodium_certified.is_(True))
        )

    rows = query.order_by(models.MenuTasteScore.review_count.desc()).limit(30).all()
    items = []
    for menu, restaurant, score in rows:
        haystack = f"{menu.name} {menu.description or ''}".lower()
        if disliked_ingredients and any(ingredient in haystack for ingredient in disliked_ingredients):
            continue

        items.append(
            schemas.RecommendationItem(
                restaurant_id=restaurant.id,
                restaurant_name=restaurant.name,
                menu_id=menu.id,
                menu_name=menu.name,
                spiciness_level=score.spiciness_level,
                saltiness_level=score.saltiness_level,
                ai_comment=(
                    f"리뷰 {score.review_count}건 기준, 맵기 {score.spiciness_level}/5 · 염도 {score.saltiness_level}/5로 분석되었습니다."
                ),
            )
        )

    return schemas.RecommendationResponse(items=items)

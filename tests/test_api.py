from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app import models

client = TestClient(app)


def reset_db():
    db = SessionLocal()
    try:
        db.query(models.ReviewSignal).delete()
        db.query(models.MenuTasteScore).delete()
        db.query(models.Menu).delete()
        db.query(models.Restaurant).delete()
        db.query(models.UserPreference).delete()
        db.commit()
    finally:
        db.close()


def test_recommendation_flow():
    reset_db()

    create_res = client.post(
        "/restaurants",
        json={
            "name": "강남 얼큰식당",
            "source_type": "Hybrid",
            "latitude": 37.4979,
            "longitude": 127.0276,
            "is_low_sodium_certified": False,
            "menus": [{"name": "육개장", "price": 10000}],
        },
    )
    assert create_res.status_code == 200
    menu_id = create_res.json()["menus"][0]["id"]

    client.post(
        f"/menus/{menu_id}/signals",
        json={"source_type": "receipt_verified", "text": "국물이 얼큰하고 좀 짰어"},
    )
    client.post(
        f"/menus/{menu_id}/signals",
        json={"source_type": "tv", "text": "맛있게 맵고 담백하다"},
    )

    recompute_res = client.post(f"/menus/{menu_id}/recompute-score")
    assert recompute_res.status_code == 200
    assert recompute_res.json()["review_count"] == 2

    pref_res = client.post(
        "/users/preferences",
        json={
            "user_key": "u1",
            "spicy_tolerance": 4,
            "sodium_sensitivity": True,
            "disliked_ingredients": ["고수"],
        },
    )
    assert pref_res.status_code == 200

    rec_res = client.post(
        "/recommendations",
        json={"user_key": "u1", "min_spiciness": 2.0, "max_spiciness": 5.0},
    )
    assert rec_res.status_code == 200
    items = rec_res.json()["items"]
    assert len(items) == 1
    assert items[0]["menu_name"] == "육개장"


def test_recommendation_excludes_disliked_ingredients():
    reset_db()

    create_res = client.post(
        "/restaurants",
        json={
            "name": "홍대 한식집",
            "source_type": "Hybrid",
            "latitude": 37.5572,
            "longitude": 126.9245,
            "is_low_sodium_certified": True,
            "menus": [
                {"name": "고수 쌀국수", "price": 9000, "description": "신선한 고수가 올라간 쌀국수"},
                {"name": "된장찌개", "price": 8500, "description": "구수한 국물"},
            ],
        },
    )
    assert create_res.status_code == 200

    menus = create_res.json()["menus"]
    for menu in menus:
        client.post(
            f"/menus/{menu['id']}/signals",
            json={"source_type": "general", "text": "적당히 맵고 담백함"},
        )
        recompute_res = client.post(f"/menus/{menu['id']}/recompute-score")
        assert recompute_res.status_code == 200

    pref_res = client.post(
        "/users/preferences",
        json={
            "user_key": "u-dislike",
            "spicy_tolerance": 3,
            "sodium_sensitivity": False,
            "disliked_ingredients": ["고수"],
        },
    )
    assert pref_res.status_code == 200

    rec_res = client.post(
        "/recommendations",
        json={"user_key": "u-dislike", "min_spiciness": 1.0, "max_spiciness": 5.0},
    )
    assert rec_res.status_code == 200

    menu_names = [item["menu_name"] for item in rec_res.json()["items"]]
    assert "고수 쌀국수" not in menu_names
    assert "된장찌개" in menu_names

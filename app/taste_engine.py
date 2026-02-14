from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import math
from typing import Iterable

from app import models

SPICY_KEYWORDS = {
    1: ["안 맵", "하나도 안 매워", "순한맛"],
    2: ["매콤", "살짝 맵"],
    3: ["칼칼", "얼큰"],
    4: ["많이 맵", "땀이 난다", "혀가 아프"],
    5: ["죽음의 맛", "불닭", "엽떡 수준"],
}

SALTY_KEYWORDS = {
    1: ["슴슴", "담백", "삼삼", "저염"],
    2: ["간이 딱", "적당히 짭짤"],
    3: ["보통 간"],
    4: ["짰", "간이 세", "자극적"],
    5: ["소태", "소금국"],
}

SWEET_KEYWORDS = {
    1: ["안 달", "당도 낮"],
    2: ["은은하게 달"],
    3: ["달달"],
    4: ["많이 달"],
    5: ["너무 달", "설탕 맛", "물린다"],
}

SOURCE_WEIGHT = {
    "tv": 1.7,
    "receipt_verified": 1.4,
    "blog": 1.1,
    "general": 1.0,
}


@dataclass
class ParsedTaste:
    spiciness: float
    saltiness: float
    sweetness: float


def _keyword_to_score(text: str, mapping: dict[int, list[str]], default: float = 3.0) -> float:
    matches = []
    lowered = text.lower()
    for score, keywords in mapping.items():
        for keyword in keywords:
            if keyword in lowered:
                matches.append(score)
    if not matches:
        return default
    return float(sum(matches) / len(matches))


def parse_taste_from_text(text: str) -> ParsedTaste:
    return ParsedTaste(
        spiciness=_keyword_to_score(text, SPICY_KEYWORDS),
        saltiness=_keyword_to_score(text, SALTY_KEYWORDS),
        sweetness=_keyword_to_score(text, SWEET_KEYWORDS),
    )


def _recency_weight(created_at: datetime) -> float:
    now = datetime.now(timezone.utc)
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    age_days = max((now - created_at).days, 0)
    return math.exp(-age_days / 90)


def aggregate_menu_scores(signals: Iterable[models.ReviewSignal]) -> tuple[float, float, float, int]:
    signals = list(signals)
    if not signals:
        return 3.0, 3.0, 3.0, 0

    spicy_sum = salty_sum = sweet_sum = 0.0
    weight_sum = 0.0
    for signal in signals:
        parsed = parse_taste_from_text(signal.text)
        weight = SOURCE_WEIGHT.get(signal.source_type, 1.0) * _recency_weight(signal.created_at)
        spicy_sum += parsed.spiciness * weight
        salty_sum += parsed.saltiness * weight
        sweet_sum += parsed.sweetness * weight
        weight_sum += weight

    return (
        round(spicy_sum / weight_sum, 2),
        round(salty_sum / weight_sum, 2),
        round(sweet_sum / weight_sum, 2),
        len(signals),
    )

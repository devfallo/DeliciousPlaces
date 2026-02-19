# DeliciousPlaces 핵심 구현 설계서

## 1. 목표
지도앱/배달앱 리뷰를 메뉴 단위로 수집·정규화하고, 식당별 맛 특성 및 핵심 키워드를 비교 가능한 형태로 제공합니다.

## 2. 핵심 요구사항 매핑
- 동일 메뉴(예: 김치찌개)를 식당별로 비교
- 리뷰 문장에서 핵심 키워드 추출(예: 돼지고기, 참치, 매운맛)
- 웹페이지에서 조회 가능
- 백엔드 API 미연결 환경(정적 미리보기)에서도 화면이 깨지지 않도록 처리

## 3. 시스템 구성
- **수집 레이어(API 입력)**
  - `POST /menus/{menu_id}/signals`
  - `source_type`: `map_app`, `delivery_app` 포함
  - `source_platform`: `google_maps`, `naver_map`, `baemin` 등 원천 플랫폼 식별
- **분석 레이어(룰 기반 MVP)**
  - 리뷰 텍스트 → 맛 점수(맵기/짠맛/단맛)
  - 리뷰 텍스트 → 태그 키워드 빈도 집계
  - 메뉴별 요약문 생성
- **조회 레이어(인사이트 API)**
  - `GET /insights/dishes/{dish_name}`
  - 메뉴명 일치 목록을 식당별 카드 데이터로 반환
- **프론트 레이어(대시보드)**
  - 메뉴명 검색
  - 카드 렌더링(점수/키워드/요약)
  - API 실패 시 예시 데이터 fallback

## 4. 데이터 모델 설계 포인트
- `ReviewSignal.source_platform` 추가로, source_type 내부 세분화 가능
- 추후 플랫폼별 신뢰도 가중치 확장 여지 확보

## 5. API 계약
### 5.1 입력 API
`POST /menus/{menu_id}/signals`
```json
{
  "source_type": "map_app",
  "source_platform": "google_maps",
  "text": "돼지고기 국물이 진하고 매콤해요"
}
```

### 5.2 조회 API
`GET /insights/dishes/김치찌개`
```json
{
  "dish_name": "김치찌개",
  "items": [
    {
      "restaurant_name": "A식당",
      "menu_name": "김치찌개",
      "review_count": 18,
      "spiciness_level": 4.2,
      "saltiness_level": 3.1,
      "sweetness_level": 2.1,
      "top_keywords": ["돼지고기", "매운맛", "국물"],
      "summary": "김치찌개은(는) 돼지고기, 매운맛 중심의 반응이 많았습니다."
    }
  ]
}
```

## 6. 오류/예외 처리 전략
- 메뉴 미존재: `404 Menu not found`
- 인사이트 데이터 없음: 빈 items 반환
- 정적 배포/미리보기에서 API 미연결 시: fallback 샘플 카드 노출 + 경고 문구 표시
- `/docs` 경로 직접 접근 시에도 랜딩 페이지 반환

## 7. 확장 로드맵
1. 플랫폼별/시간대별 가중치 고도화
2. 키워드 사전 동의어 처리(예: 고수=실란트로)
3. LLM 요약기로 문장 품질 개선
4. 배치 수집 파이프라인(크롤링/중복제거/스팸필터)

# DeliciousPlaces

초개인화 미각 취향 기반 맛집/메뉴 추천 플랫폼의 MVP 백엔드입니다.

## 핵심 구현 범위
- FastAPI 기반 REST API
- 식당/메뉴/미각 점수/사용자 취향 데이터 모델
- 미각 온톨로지 기반 리뷰 문장 점수화 휴리스틱
- 메뉴 단위 추천 API (맵기 슬라이더 + 저염 필터)
- 시간/출처 가중치를 반영한 메뉴 미각 점수 집계

## 실행
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 테스트
```bash
pytest -q
```

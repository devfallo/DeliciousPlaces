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

## GitHub Pages 배포
이 저장소는 `docs/` 폴더를 GitHub Pages로 자동 배포하도록 워크플로를 포함합니다.

1. GitHub 저장소 기본 브랜치가 `main`인지 확인
2. 저장소 **Settings → Pages → Source**에서 **GitHub Actions** 선택
3. `main` 브랜치에 푸시하면 `Deploy GitHub Pages` 워크플로가 자동 실행

배포 URL 형식:
- 개인 계정 저장소: `https://<github-username>.github.io/DeliciousPlaces/`
- 조직 저장소: `https://<org-name>.github.io/DeliciousPlaces/`

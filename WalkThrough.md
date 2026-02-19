# DeliciousPlaces 구현 WalkThrough

## 1) 현재 상태 요약
- FastAPI 기반 핵심 API(`restaurants`, `users/preferences`, `menus/*`, `recommendations`)가 동작합니다.
- 메뉴별 인사이트 API(`GET /insights/dishes/{dish_name}`)를 통해 같은 메뉴의 식당별 비교가 가능합니다.
- 웹페이지는 API 연결이 어려운 미리보기 환경에서도 fallback 예시 데이터를 렌더링합니다.

## 2) 이번 업데이트
- **미리보기 Not found 대응**
  - `/docs` 경로 접근 시에도 랜딩 페이지를 반환하도록 라우트를 추가했습니다.
  - 정적 환경(예: GitHub Pages)에서 백엔드 API 호출이 불가능할 때 `Not found`/빈 화면 대신 예시 카드가 표시되도록 프론트 fallback 처리했습니다.
- **요청사항 문서화**
  - `CORE_IMPLEMENTATION_DESIGN.md` 파일로 핵심 구현 설계서 작성 완료.

## 3) 진행률 업데이트
- [x] 식당/메뉴 생성 API
- [x] 사용자 취향 저장 API
- [x] 리뷰 신호 적재 API (map_app/delivery_app + source_platform)
- [x] 미각 점수 재계산 API
- [x] 맵기/저염 기반 추천 API
- [x] 사용자 비선호 재료 기반 추천 제외 로직
- [x] 메뉴별 인사이트 조회 API
- [x] 미리보기(정적 환경) fallback UI
- [ ] 플랫폼별 리뷰 수집 자동화 파이프라인(크롤링/ETL)
- [ ] 인증/권한(로그인, 사용자 분리)

## 4) 다음 작업 제안
1. 실제 리뷰 수집 커넥터(지도앱/배달앱)와 비동기 수집 큐 구성
2. 키워드 추출을 사전 기반 + 임베딩 기반 하이브리드로 고도화
3. 플랫폼/리뷰 신뢰도별 가중치 튜닝 대시보드 추가
4. 운영 모니터링(에러율, 수집 성공률, 분석 지연) 구축

## 5) 실행/확인 방법
```bash
PYTHONPATH=. uvicorn app.main:app --reload
```
- 로컬: `http://127.0.0.1:8000/` 또는 `http://127.0.0.1:8000/docs`
- 정적 미리보기: API 미연결 시 예시 인사이트 카드가 표시됨

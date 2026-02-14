# DeliciousPlaces 구현 Walkthrough

## 1) 현재 상태 요약
- FastAPI 기반 핵심 API(`restaurants`, `users/preferences`, `menus/*`, `recommendations`)가 동작합니다.
- 리뷰 시그널 기반 미각 점수 재계산(`recompute-score`)이 구현되어 있습니다.
- 사용자 저염 선호(`sodium_sensitivity`)에 따른 추천 필터링이 반영되어 있습니다.

## 2) 이번 턴에서 이어서 구현한 내용
- 추천 로직에 **비선호 재료(disliked_ingredients) 필터링**을 추가했습니다.
  - 사용자 선호에 등록된 비선호 재료를 소문자/공백 정규화합니다.
  - 메뉴명 + 메뉴 설명 텍스트에 비선호 재료가 포함되면 추천 결과에서 제외합니다.
- 회귀 방지를 위해 API 테스트를 추가했습니다.
  - `test_recommendation_excludes_disliked_ingredients`
  - 비선호 재료 `고수`가 포함된 메뉴가 추천에서 제외되는지 검증합니다.

## 3) 진행률 업데이트
- [x] 식당/메뉴 생성 API
- [x] 사용자 취향 저장 API
- [x] 리뷰 신호 적재 API
- [x] 미각 점수 재계산 API
- [x] 맵기/저염 기반 추천 API
- [x] 사용자 비선호 재료 기반 추천 제외 로직
- [ ] 인증/권한(로그인, 사용자 분리)
- [ ] 검색/필터 고도화(거리, 가격대, 카테고리)
- [ ] 운영 배포 파이프라인 고도화

## 4) 다음 구현 제안
1. 비선호 재료 사전/동의어(예: 고수=실란트로) 매핑 추가
2. 추천 정렬 점수 고도화(취향 일치도 + 리뷰 신뢰도)
3. 사용자별 추천 로그 저장 및 피드백 루프 구축

---
실제 웹페이지 주소: http://127.0.0.1:8000/docs


## 5) GitHub Pages 에러 해결 가이드 (사용자 설정 필요)
`actions/configure-pages@v5` 단계에서 아래 에러가 발생하는 핵심 원인은,
워크플로우 토큰(`GITHUB_TOKEN`)이 **Pages 사이트를 새로 생성/활성화할 권한이 없기 때문**입니다.

- `Get Pages site failed. Error: Not Found`
- `Create Pages site failed. Error: Resource not accessible by integration`

즉, 워크플로우가 Pages를 자동 생성하려고 시도하면 실패할 수 있으므로,
저장소에서 Pages를 먼저 수동으로 활성화하고 워크플로우는 배포만 하도록 설정해야 합니다.

### A. 저장소(Settings)에서 먼저 해야 할 설정
1. GitHub 저장소 → **Settings** → **Pages** 이동
2. **Build and deployment** 섹션에서
   - **Source**: `GitHub Actions` 선택
3. 저장(또는 자동 반영) 후 페이지가 활성화되었는지 확인

> 조직(Organization) 저장소라면, 조직 정책에서 Pages 사용이 허용되어 있어야 합니다.

### B. Actions 권한 설정 확인
1. 저장소 → **Settings** → **Actions** → **General**
2. **Workflow permissions** 를 `Read and write permissions` 로 설정
   - 최소한 Pages 배포에 필요한 write 권한이 있어야 합니다.
3. 필요 시 `Allow GitHub Actions to create and approve pull requests` 옵션은 PR 자동화가 필요할 때만 활성화

### C. 왜 워크플로우를 수정했는지
기존에는 `configure-pages` 단계에 `enablement: true`가 있어
Pages 사이트 생성 API를 호출하려고 했고, 이때 권한 부족으로 실패했습니다.

이 옵션을 제거해서,
- Pages **활성화는 저장소 설정에서 수동 1회**
- Actions는 이후 **배포만 수행**
하도록 분리했습니다.

### D. 설정 후 검증 방법
1. `main` 브랜치에 커밋 푸시
2. Actions 탭에서 `Deploy GitHub Pages` 워크플로우 실행 확인
3. `Deploy to GitHub Pages` 단계가 성공하면
4. 저장소의 `https://<owner>.github.io/<repo>/` 주소 접속 확인

### E. 계속 실패할 때 체크리스트
- 저장소가 포크라면, 포크 권한 정책으로 Pages 관련 토큰 권한이 제한될 수 있음
- Organization의 Actions/Pages 정책에서 해당 저장소가 차단되어 있지 않은지 확인
- 브랜치 보호/환경 보호 규칙으로 `github-pages` 환경 배포가 보류되지 않는지 확인
- 최초 활성화 직후에는 반영까지 수 분 소요될 수 있음

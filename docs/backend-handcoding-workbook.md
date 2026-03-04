# Backend Handcoding Workbook

이 문서는 `README`의 아래 백엔드 브랜치 범위를 손코딩으로 진행할 때 쓰는 작업 교재입니다.

- `feature/auth-signup`
- `feature/auth-login-logout`
- `feature/auth-guard`
- `feature/meetings-crud`
- `feature/meetings-query`
- `feature/meetings-join`

## 1) 파일 맵 (어디에 무엇을 작성?)

- API 엔드포인트: `app/api/auth_api.py`, `app/api/meetings_api.py`
- 비즈니스 로직: `app/services/auth_service.py`, `app/services/meeting_service.py`
- DB 접근: `app/models/user_repository.py`, `app/models/meeting_repository.py`
- 인증 미들웨어: `app/middleware/auth_guard.py`
- 테스트: `tests/integration/test_auth_*.py`, `tests/integration/test_meetings_*.py`

권장 흐름: `Route -> Service -> Repository -> MongoDB`

## 2) 브랜치별 손코딩 순서

### A. `feature/auth-signup`
1. `AuthService.signup()` 입력값 검증
2. `UserRepository.find_by_email()`로 중복 이메일 검사
3. 비밀번호 해시 후 `UserRepository.create_user()` 저장
4. `POST /api/v1/auth/signup` 성공(201)/실패(400, 409) 응답 맞추기
5. `tests/integration/test_auth_signup_api.py` 활성화

### B. `feature/auth-login-logout`
1. `AuthService.login()`에서 계정 조회 + 비밀번호 검증
2. 로그인 성공 시 세션(`session["user_id"]`) 저장
3. `AuthService.logout()`에서 세션 제거
4. `tests/integration/test_auth_login_logout_api.py` 활성화

### C. `feature/auth-guard`
1. `login_required` 데코레이터 정책 확정
2. 보호가 필요한 API에 데코레이터 적용
3. 401/403 공통 실패 포맷 통일
4. `tests/integration/test_auth_guard_api.py` 활성화

### D. `feature/meetings-crud`
1. `MeetingService.create/update/delete` 구현
2. `MeetingRepository` CRUD 쿼리 구현
3. 작성자 권한 검증(guard/서비스) 연계
4. `tests/integration/test_meetings_crud_api.py` 활성화

### E. `feature/meetings-query`
1. `MeetingService.list/get_detail` 구현
2. 필터/정렬/페이지네이션 쿼리 반영
3. `tests/integration/test_meetings_query_api.py` 활성화

### F. `feature/meetings-join`
1. `MeetingService.join/cancel_join` 구현
2. 정원 초과/중복 참여 방지 로직 추가
3. `$addToSet`/`$pull` 기반 참여 처리
4. `tests/integration/test_meetings_join_api.py` 활성화

## 3) 공통 응답 형식

실패 응답(공통):

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "에러 메시지"
  }
}
```

성공 응답은 기능별 스펙(README API 컨벤션)대로 구현합니다.

## 4) 개발/검증 명령

PowerShell:

```powershell
.\scripts\test-local.ps1
.\scripts\test-local.ps1 tests/integration/test_auth_signup_api.py -q
```

macOS/Linux:

```bash
bash ./scripts/test-local.sh
bash ./scripts/test-local.sh tests/integration/test_auth_signup_api.py -q
```

## 5) 작업 규칙

- 한 브랜치에 한 기능 목표만 담기
- Route 파일에서는 파싱/응답만, 핵심 규칙은 Service로 이동
- DB 쿼리는 Repository로 고정
- PR에 테스트 결과를 반드시 남기기

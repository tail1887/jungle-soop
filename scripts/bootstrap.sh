#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

echo "[bootstrap] 프로젝트 루트: $REPO_ROOT"

if [[ ! -f ".venv/bin/python" ]]; then
  echo "[bootstrap] 가상환경(.venv) 생성"
  python3 -m venv .venv
else
  echo "[bootstrap] 가상환경(.venv) 이미 존재"
fi

echo "[bootstrap] pip 최신화"
.venv/bin/python -m pip install --upgrade pip

echo "[bootstrap] 개발 의존성 설치(requirements-dev.txt)"
.venv/bin/pip install -r requirements-dev.txt

if [[ ! -f ".env" ]]; then
  if [[ -f ".env.example" ]]; then
    echo "[bootstrap] .env 파일 생성(.env.example 복사)"
    cp .env.example .env
  else
    echo "[bootstrap] .env.example 없음 -> 기본 .env 생성"
    cat > .env <<EOF
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=change-this-secret
MONGO_URI=mongodb://localhost:27017/jungle_soop
EOF
  fi
else
  echo "[bootstrap] .env 파일 이미 존재"
fi

echo
echo "완료: 개발 시작 준비가 끝났습니다."
echo "다음 명령(현재 셸 세션): source .venv/bin/activate"
echo "로컬 테스트 실행: bash ./scripts/test-local.sh"

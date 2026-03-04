#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/jungle-soop}"
REPO_URL="${REPO_URL:-https://github.com/tail1887/jungle-soop.git}"
BRANCH="${BRANCH:-main}"
DOCKER_BIN="${DOCKER_BIN:-docker}"

echo "[deploy] app dir: $APP_DIR"
echo "[deploy] branch: $BRANCH"

if [[ ! -d "$APP_DIR/.git" ]]; then
  echo "[deploy] repository not found. cloning..."
  git clone "$REPO_URL" "$APP_DIR"
fi

cd "$APP_DIR"

echo "[deploy] syncing repository..."
git fetch origin
git checkout "$BRANCH"
# 배포 서버의 로컬 변경 상태에 영향받지 않도록 원격 브랜치 상태로 강제 동기화
git reset --hard "origin/$BRANCH"
git clean -fd

if [[ -f ".env.example" && ! -f ".env" ]]; then
  echo "[deploy] creating .env from .env.example"
  cp .env.example .env
fi

ensure_docker() {
  if command -v docker >/dev/null 2>&1; then
    if docker compose version >/dev/null 2>&1; then
      DOCKER_BIN="docker"
      return
    fi
  fi

  echo "[deploy] docker/compose not available. installing..."
  if command -v sudo >/dev/null 2>&1; then
    sudo apt-get update -y
    sudo apt-get install -y ca-certificates curl gnupg lsb-release
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker "$USER" || true
    DOCKER_BIN="sudo docker"
  else
    apt-get update -y
    apt-get install -y ca-certificates curl gnupg lsb-release
    curl -fsSL https://get.docker.com | sh
    DOCKER_BIN="docker"
  fi
}

ensure_docker

echo "[deploy] running docker compose..."
$DOCKER_BIN compose -f docker/docker-compose.yml up -d --build

echo "[deploy] done."

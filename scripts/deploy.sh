#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-$HOME/jungle-soop}"
REPO_URL="${REPO_URL:-https://github.com/tail1887/jungle-soop.git}"
BRANCH="${BRANCH:-main}"

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
git pull origin "$BRANCH"

if [[ -f ".env.example" && ! -f ".env" ]]; then
  echo "[deploy] creating .env from .env.example"
  cp .env.example .env
fi

echo "[deploy] running docker compose..."
docker compose -f docker/docker-compose.yml up -d --build

echo "[deploy] done."

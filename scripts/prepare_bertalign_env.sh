#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

export UV_CACHE_DIR="${UV_CACHE_DIR:-/tmp/uv-cache}"
export HF_HOME="${HF_HOME:-$ROOT_DIR/.cache/huggingface}"
export SENTENCE_TRANSFORMERS_HOME="${SENTENCE_TRANSFORMERS_HOME:-$HF_HOME}"
export TRANSFORMERS_CACHE="${TRANSFORMERS_CACHE:-$HF_HOME/transformers}"
export HF_HUB_DISABLE_TELEMETRY=1

if [[ -n "${BOOKALIGN_USE_PROXY_10808:-}" ]]; then
  export HTTP_PROXY="${HTTP_PROXY:-http://127.0.0.1:10808}"
  export HTTPS_PROXY="${HTTPS_PROXY:-http://127.0.0.1:10808}"
fi

mkdir -p "$UV_CACHE_DIR" "$HF_HOME" "$TRANSFORMERS_CACHE"

cd "$ROOT_DIR"
uv sync --group dev --group align
uv run python - <<'PY'
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/LaBSE")
print("model_loaded", model.__class__.__name__)
print("device", getattr(model, "device", "unknown"))
PY

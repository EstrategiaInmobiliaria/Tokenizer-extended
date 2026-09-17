#!/usr/bin/env bash
# Idempotent bootstrap for the Tokenizer-extended repository.
# Sets up three runnable components:
#   1. Tiktokenizer  - Next.js (T3) web app (Node)
#   2. Plotting toolkit - NumPy/Matplotlib scripts at the repo root (Python)
#   3. master_blueprint - FastAPI financial-analysis API (Python)
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# --- System dependency: Python venv support (only if missing) ---
if ! python3 -c "import ensurepip" >/dev/null 2>&1; then
  sudo apt-get update -qq
  sudo apt-get install -y -qq python3.12-venv
fi

# --- Node dependencies (Tiktokenizer web app) ---
yarn install --frozen-lockfile

# --- Python virtualenv + dependencies (plotting toolkit + master_blueprint API) ---
python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -r master_blueprint/requirements.txt

# --- Local env defaults for the web app ---
# SKIP_ENV_VALIDATION lets the app run without a HuggingFace API key; the core
# OpenAI tokenizers work fully client-side. A real HF_API_KEY (provided as a
# secret) is still picked up from the environment for open-source model prefetch.
if [ ! -f .env ]; then
  echo "SKIP_ENV_VALIDATION=1" > .env
fi

# --- Best-effort tokenizer prefetch ---
# Caches publicly-downloadable tokenizers into public/hf. Gated models
# (e.g. meta-llama, gemma) require a licensed HF_API_KEY and are skipped;
# the app remains fully functional without them.
SKIP_ENV_VALIDATION=1 yarn dotenv tsx src/scripts/download.ts \
  || echo "Note: HuggingFace tokenizer prefetch incomplete (gated models need a licensed HF_API_KEY). Core app still works."

echo "Install complete."

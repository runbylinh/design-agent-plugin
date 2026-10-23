#!/bin/bash
# Cài Image Agent trên Mac (chip Apple hoặc Intel) / Linux — KHÔNG cần mật khẩu, KHÔNG cần Homebrew.
# Cài vào ~/.image-agent (dùng chung cho mọi studio, giữ nguyên khi cập nhật plugin).
set -e
ENGINE="$(cd "$(dirname "$0")" && pwd)"
RT="${IMAGE_AGENT_HOME:-$HOME/.image-agent}"
say() { printf "\n▶ %s\n" "$1"; }

case "$(uname -s)-$(uname -m)" in
  Darwin-arm64) PLAT=osx-arm64 ;;
  Darwin-x86_64) PLAT=osx-64 ;;
  Linux-x86_64) PLAT=linux-64 ;;
  Linux-aarch64) PLAT=linux-aarch64 ;;
  *) echo "❌ Máy chưa được hỗ trợ: $(uname -s)-$(uname -m)"; exit 1 ;;
esac
mkdir -p "$RT/tools/bin" "$RT/fonts" "$RT/icons"
MM="$RT/tools/bin/micromamba"
if [ ! -x "$MM" ]; then
  if [ -x "$HOME/.video-agent/tools/bin/micromamba" ]; then
    cp "$HOME/.video-agent/tools/bin/micromamba" "$MM"          # máy đã cài video-edit: dùng lại
  else
    say "Tải micromamba (cài Python không cần mật khẩu)…"
    curl -Ls "https://micro.mamba.pm/api/micromamba/$PLAT/latest" | tar -xj -C "$RT/tools" bin/micromamba
  fi
fi
if [ ! -x "$RT/env/bin/python" ]; then
  say "Cài Python 3.12 vào $RT/env (vài phút)…"
  MAMBA_ROOT_PREFIX="$RT/tools/mamba" "$MM" create -y -q -p "$RT/env" -c conda-forge python=3.12
fi
PY="$RT/env/bin/python"
say "Cài thư viện Python (dựng ảnh, tách nền)…"
"$PY" -m pip install -q -r "$ENGINE/requirements.txt"
say "Cài Chromium (xuất ảnh)…"
"$PY" -m playwright install chromium
say "Tải font mặc định + bộ biểu tượng…"
"$PY" "$ENGINE/ia.py" font get "Be Vietnam Pro" || true
"$PY" "$ENGINE/ia.py" icons install || true
say "Kiểm tra:"
"$PY" "$ENGINE/ia.py" doctor || true
echo
echo "✅ Cài xong. Model tách nền (~170MB) sẽ tự tải ở lần tách nền đầu tiên."

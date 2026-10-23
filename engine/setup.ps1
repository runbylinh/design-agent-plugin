# Cai Agent 02 Anh (image-agent) tren Windows 10/11 - KHONG can quyen Administrator.
# Cai vao %USERPROFILE%\.image-agent (dung chung moi studio, giu nguyen khi cap nhat plugin).
$ErrorActionPreference = "Stop"
$ENGINE = $PSScriptRoot
$RT = if ($env:IMAGE_AGENT_HOME) { $env:IMAGE_AGENT_HOME } else { Join-Path $env:USERPROFILE ".image-agent" }
function Say($m) { Write-Host "`n> $m" -ForegroundColor Cyan }

$tools = Join-Path $RT "tools"
New-Item -ItemType Directory -Force $tools | Out-Null
$mm = Join-Path $tools "micromamba.exe"
if (-not (Test-Path $mm)) {
  $shared = Join-Path $env:USERPROFILE ".video-agent\tools\micromamba.exe"
  if (Test-Path $shared) { Copy-Item $shared $mm }
  else {
    Say "Tai micromamba (cai Python)..."
    $arc = Join-Path $tools "micromamba.tar.bz2"
    Invoke-WebRequest -UseBasicParsing "https://micro.mamba.pm/api/micromamba/win-64/latest" -OutFile $arc
    tar -xf $arc -C $tools Library/bin/micromamba.exe
    Move-Item (Join-Path $tools "Library\bin\micromamba.exe") $mm
    Remove-Item $arc
  }
}
$envDir = Join-Path $RT "env"
$py = Join-Path $envDir "python.exe"
if (-not (Test-Path $py)) {
  Say "Cai Python 3.12 (vai phut)..."
  $env:MAMBA_ROOT_PREFIX = Join-Path $tools "mamba"
  & $mm create -y -q -p $envDir -c conda-forge python=3.12
  if ($LASTEXITCODE -ne 0) { throw "Cai Python loi" }
}
$env:PYTHONUTF8 = "1"
Say "Cai thu vien Python (dung anh, tach nen)..."
& $py -m pip install -q -r (Join-Path $ENGINE "requirements.txt")
Say "Cai Chromium (xuat anh)..."
& $py -m playwright install chromium
Say "Tai font mac dinh + bo bieu tuong..."
& $py (Join-Path $ENGINE "ia.py") font get "Be Vietnam Pro"
& $py (Join-Path $ENGINE "ia.py") icons install
Say "Kiem tra:"
& $py (Join-Path $ENGINE "ia.py") doctor
Write-Host "`nCai xong. Model tach nen (~170MB) se tu tai o lan tach nen dau tien." -ForegroundColor Green

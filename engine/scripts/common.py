"""Dùng chung: đường dẫn plugin/runtime/studio, đọc ghi JSON, thông báo."""
import hashlib
import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

ENGINE = Path(__file__).resolve().parent.parent
PLUGIN = ENGINE.parent
RUNTIME = Path(os.environ.get("IMAGE_AGENT_HOME", Path.home() / ".image-agent"))
STUDIO_FILE = "image-studio.json"


class IAError(Exception):
    pass


def die(msg, code=1):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(code)


def info(msg):
    print(msg, flush=True)


def warn(msg):
    print(f"⚠️ {msg}", flush=True)


def read_json(path, default=None):
    p = Path(path)
    if not p.exists():
        if default is not None:
            return default
        die(f"Không thấy file {p}")
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        die(f"{p.name} sai cú pháp JSON (dòng {e.lineno}, cột {e.colno}): {e.msg}")


def write_json(path, data):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def slug(text):
    t = unicodedata.normalize("NFD", str(text)).encode("ascii", "ignore").decode().lower()
    t = t.replace("đ", "d")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:48] or "x"


def norm_text(text):
    """Chuẩn hoá chữ để so 'đúng chữ đã duyệt': bỏ **nhấn**, xuống dòng, khoảng trắng thừa, NFC."""
    t = unicodedata.normalize("NFC", str(text or ""))
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def text_hash(text):
    return hashlib.sha256(norm_text(text).encode("utf-8")).hexdigest()[:16]


def file_hash(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ------------------------------------------------------------------ studio

def find_studio(start=None):
    env = os.environ.get("IMAGE_STUDIO")
    if env and (Path(env) / STUDIO_FILE).exists():
        return Path(env).resolve()
    d = Path(start or Path.cwd()).resolve()
    for p in [d, *d.parents]:
        if (p / STUDIO_FILE).exists():
            return p
    die("Chưa ở trong studio ảnh nào (không thấy image-studio.json). Chạy `ia studio init <thư-mục>` hoặc cd vào studio.")


def studio_config(st=None):
    st = st or find_studio()
    cfg = read_json(st / STUDIO_FILE)
    cfg["_dir"] = str(st)
    return cfg


def save_studio_config(cfg):
    data = {k: v for k, v in cfg.items() if not k.startswith("_")}
    write_json(Path(cfg["_dir"]) / STUDIO_FILE, data)


# ------------------------------------------------------------------ job

JOB_RE = re.compile(r"^DS-\d{6}-\d{2,3}$")


def job_dir(job_id, st=None):
    st = st or find_studio()
    if not JOB_RE.match(job_id):
        die(f"Mã job '{job_id}' không đúng dạng DS-YYMMDD-NN.")
    d = st / "jobs" / job_id
    if not d.exists():
        die(f"Không thấy job {job_id} trong {st / 'jobs'}. Xem `ia status` hoặc `ia job find <từ khoá>`.")
    return d


def manifest(job_id, st=None):
    d = job_dir(job_id, st)
    m = read_json(d / "manifest.json")
    m["_dir"] = str(d)
    return m


def save_manifest(m):
    data = {k: v for k, v in m.items() if not k.startswith("_")}
    data["cap_nhat"] = now()
    write_json(Path(m["_dir"]) / "manifest.json", data)


def version_dir(m, v=None):
    v = v or m.get("phien_ban_hien_tai") or 1
    return Path(m["_dir"]) / f"v{int(v)}"


def log(m, text):
    m.setdefault("nhat_ky", []).append(f"{now()} · {text}")

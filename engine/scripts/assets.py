"""Thư viện tài nguyên (Asset Registry), font, biểu tượng.

  ia assets find <từ khoá…> [--loai logo|element|anh|mau] [--brand ten-brand]   tìm trong Brand Kit + Media Assets đã đăng ký
  ia assets add <file> --loai <logo|element|anh|mau> --tag "a,b" [--ten "…"] [--quyen noi-bo|thuong-mai|chua-ro] [--drive-id …]
  ia assets list [--loai …]
  ia assets scan <thư mục>          đăng ký hàng loạt ảnh trong một thư mục (tag theo tên file + thư mục)
  ia font get "<Tên font Google>"    tải font (mọi độ đậm) từ Google Fonts về ~/.image-agent/fonts
  ia icons install | ia icons find <từ khoá>     bộ biểu tượng Lucide (giấy phép ISC, dùng thương mại được)

Registry là file _assets.json ở thư mục studio (và trong Brand Kit nếu có). Mỗi mục:
  {"id":"AS-001","loai":"logo","ten":"Logo tím nền trong suốt","file":"…","drive_id":"…","tag":["logo","tim"],
   "brand":"ten-brand","trang_thai":"Đã duyệt","quyen":"noi-bo","phien_ban":"v1"}
Không tự sửa file gốc: mọi xử lý làm trên bản sao trong job.
"""
import json
import re
import subprocess
import tarfile
import urllib.request
from pathlib import Path

from common import RUNTIME, die, find_studio, info, read_json, slug, studio_config, warn, write_json

IMG = (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".heic")
NHOM_LOAI = {"Logo & nhận diện": "logo", "Người": "anh", "Sản phẩm - Dịch vụ": "anh", "Bối cảnh": "anh",
             "Đồ hoạ & thành phần": "element", "Tham khảo": "mau", "Theo việc": "anh"}
LOAI_NHOM = {"logo": "Logo & nhận diện", "element": "Đồ hoạ & thành phần", "mau": "Tham khảo", "anh": "Người"}


def opt(args, name, default=None):
    return args[args.index(name) + 1] if name in args else default


def registries():
    cfg = studio_config()
    regs = [Path(cfg["_dir"]) / "_assets.json"]
    for name, d in cfg.get("brand_kits", {}).items():
        regs.append(Path(d).expanduser() / "_assets.json")
    ma = (cfg.get("drive") or {}).get("sync_root")
    if ma:
        regs.append(Path(ma).expanduser() / "_assets.json")
    return regs


def load_all():
    items = []
    for r in registries():
        for it in read_json(r, {"items": []}).get("items", []):
            it["_reg"] = str(r)
            items.append(it)
    # tab 02 Source của Sheet (bộ đệm sau `ia sheet pull Source`)
    import tracker
    cfg = studio_config()
    if tracker.connected(cfg):
        have = {it.get("id") for it in items}
        for r in tracker.cache("Source", cfg)["rows"]:
            if r.get("AS ID") and r["AS ID"] not in have:
                items.append({"id": r["AS ID"], "loai": NHOM_LOAI.get(r.get("Nhóm", ""), "anh"), "nhom": r.get("Nhóm", ""),
                              "ten": r.get("Tên", ""), "file": "", "drive_id": r.get("Drive File ID", ""), "link": r.get("Link Drive", ""),
                              "tag": [t.strip() for t in str(r.get("Tag", "")).split(",") if t.strip()], "brand": "",
                              "trang_thai": r.get("Trạng thái", ""), "quyen": r.get("Quyền dùng", "Chưa rõ"), "_reg": "(Sheet 02 Source)"})
    # Brand Kit: logo/ và anh-mau/ tự coi là tài nguyên dù chưa đăng ký
    known = {it.get("file") for it in items}
    for name, d in cfg.get("brand_kits", {}).items():
        d = Path(d).expanduser()
        for sub, loai in (("logo", "logo"), ("anh-mau", "mau"), ("thanh-phan", "element"), ("mau", "mau")):
            for f in sorted((d / sub).glob("*")) if (d / sub).exists() else []:
                if f.suffix.lower() in IMG + (".json",) and str(f) not in known:
                    items.append({"id": "", "loai": loai, "ten": f.stem, "file": str(f), "tag": re.split(r"[-_ ]+", slug(f.stem)),
                                  "brand": name, "trang_thai": "Đã duyệt", "quyen": "noi-bo", "_reg": "(Brand Kit)"})
    return items


def score(it, words):
    hay = " ".join([it.get("ten", ""), " ".join(it.get("tag", [])), Path(it.get("file", "")).stem, it.get("loai", "")])
    hay = hay.lower() + " " + slug(hay).replace("-", " ")
    return sum(1 for w in words if w in hay)


def find(args):
    words = [slug(w).replace("-", " ") for w in args if not w.startswith("--")]
    words = [w for w in " ".join(words).split() if w]
    loai, brand = opt(args, "--loai"), opt(args, "--brand")
    for flag in ("--loai", "--brand"):
        if flag in args:
            v = opt(args, flag)
            words = [w for w in words if w != slug(v).replace("-", " ")]
    hits = []
    for it in load_all():
        if loai and it.get("loai") != loai:
            continue
        if brand and it.get("brand") not in (brand, None, ""):
            continue
        s = score(it, words) if words else 1
        if s:
            hits.append((s, it))
    hits.sort(key=lambda x: (-x[0], x[1].get("trang_thai") != "Đã duyệt"))
    if not hits:
        info("Không thấy tài nguyên khớp. Báo người dùng thiếu tài nguyên — không tự lấy ảnh không liên quan.")
        return 1
    for s, it in hits[:15]:
        where = it.get("file") or it.get("link") or ("drive:" + it.get("drive_id", ""))
        exists = "" if not it.get("file") or Path(it["file"]).expanduser().exists() else "  ⚠️ file không còn trên máy"
        info(f"{it.get('id') or '—':7s} [{it.get('loai')}] {it.get('ten')}  · tag: {', '.join(it.get('tag', []))}"
             f"  · {it.get('trang_thai', '')} · quyền {it.get('quyen', 'chua-ro')}\n         {where}{exists}")
    return 0


def add(args):
    if not args:
        die(__doc__)
    f = Path(args[0]).expanduser()
    drive_id = opt(args, "--drive-id", "")
    if not f.exists() and not drive_id:
        die(f"Không thấy {f}")
    reg = Path(studio_config()["_dir"]) / "_assets.json"
    data = read_json(reg, {"items": []})
    import tracker
    ids = [x["id"] for x in data["items"] if x.get("id", "").startswith("AS-")]
    if tracker.connected():
        ids += [r["AS ID"] for r in tracker.cache("Source")["rows"] if str(r.get("AS ID", "")).startswith("AS-")]
    n = 1 + max([int(i.split("-")[1]) for i in ids if i.split("-")[1].isdigit()] or [0])
    it = {"id": f"AS-{n:03d}", "loai": opt(args, "--loai") or die("Thiếu --loai"), "ten": opt(args, "--ten", f.stem),
          "file": str(f.resolve()) if f.exists() else "", "drive_id": drive_id,
          "tag": [t.strip() for t in (opt(args, "--tag", "")).split(",") if t.strip()],
          "brand": opt(args, "--brand", studio_config().get("brand_mac_dinh", "")), "trang_thai": opt(args, "--trang-thai", "Đã duyệt"),
          "quyen": opt(args, "--quyen", "chua-ro"), "phien_ban": opt(args, "--phien-ban", "v1")}
    data["items"].append(it)
    write_json(reg, data)
    import tracker
    from common import now
    nhom = opt(args, "--nhom", LOAI_NHOM.get(it["loai"], "Người"))
    link = opt(args, "--link", f"https://drive.google.com/file/d/{drive_id}/view" if drive_id else "")
    quyen = {"noi-bo": "Nội bộ", "thuong-mai": "Thương mại"}.get(it["quyen"], "Chưa rõ")
    tracker.upsert("Source", it["id"], {"Nhóm": nhom, "Tên": it["ten"], "Tag": ", ".join(it["tag"]), "Link Drive": link,
                                        "Drive File ID": drive_id, "Quyền dùng": quyen,
                                        "Trạng thái": "Đã duyệt" if it["trang_thai"] == "Đã duyệt" else "Chưa kiểm",
                                        "Người cung cấp": opt(args, "--nguoi", ""), "Ngày thêm": now()[:10]})
    info(f"Đã đăng ký {it['id']} — {it['ten']}")
    tracker.hint_push()
    return 0


def scan(args):
    root = Path(args[0]).expanduser() if args else die("ia assets scan <thư mục>")
    reg = Path(studio_config()["_dir"]) / "_assets.json"
    data = read_json(reg, {"items": []})
    known = {x.get("file") for x in data["items"]}
    n = 1 + max([int(x["id"].split("-")[1]) for x in data["items"] if x.get("id", "").startswith("AS-")] or [0])
    added = 0
    for f in sorted(root.rglob("*")):
        if f.suffix.lower() not in IMG or str(f.resolve()) in known or f.name.startswith("."):
            continue
        parts = [slug(p) for p in f.relative_to(root).parts]
        tags = sorted({t for p in parts for t in p.split("-") if len(t) > 1})
        low = " ".join(parts)
        loai = "logo" if "logo" in low else "element" if any(k in low for k in ("icon", "element", "khung", "nen", "background")) \
            else "mau" if any(k in low for k in ("approved", "mau", "template")) else "anh"
        data["items"].append({"id": f"AS-{n:03d}", "loai": loai, "ten": f.stem, "file": str(f.resolve()), "drive_id": "",
                              "tag": tags, "brand": studio_config().get("brand_mac_dinh", ""), "trang_thai": "Chưa rõ",
                              "quyen": "chua-ro", "phien_ban": "v1"})
        n += 1
        added += 1
    write_json(reg, data)
    info(f"Đã đăng ký thêm {added} tài nguyên từ {root}. Nên bổ sung tag cho ảnh người (tên người), trạng thái và quyền sử dụng.")
    return 0


def list_(args):
    loai = opt(args, "--loai")
    for it in load_all():
        if not loai or it.get("loai") == loai:
            info(f"{it.get('id') or '—':7s} [{it.get('loai')}] {it.get('ten')} · {', '.join(it.get('tag', []))}")
    return 0


# ------------------------------------------------------------------ font

def font_get(args):
    fam = " ".join(a for a in args if not a.startswith("--")) or die('ia font get "Be Vietnam Pro"')
    key = re.sub(r"[^a-z0-9]", "", fam.lower())
    dest = RUNTIME / "fonts" / slug(fam)
    dest.mkdir(parents=True, exist_ok=True)
    got = 0
    for lic in ("ofl", "apache", "ufl"):
        api = f"https://api.github.com/repos/google/fonts/contents/{lic}/{key}"
        try:
            with urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": "image-agent"}), timeout=30) as r:
                files = json.load(r)
        except Exception:  # noqa: BLE001
            continue
        for f in files:
            name = f["name"]
            if not name.lower().endswith((".ttf", ".otf")) or "italic" in name.lower():
                continue
            target = dest / name
            if not target.exists():
                urllib.request.urlretrieve(f["download_url"], target)
            got += 1
        if got:
            break
    if not got:
        die(f"Không tìm thấy '{fam}' trên Google Fonts. Font thương mại → chép file .ttf/.otf vào Brand Kit/fonts/.")
    if any("[" in p.name for p in dest.iterdir()):
        warn("Font dạng 'variable' (một file nhiều độ đậm) — trình duyệt vẫn dùng được đủ độ đậm.")
    info(f"Đã có {got} file font '{fam}' → {dest}")
    return 0


# ------------------------------------------------------------------ icons

def icons(args):
    d = RUNTIME / "icons"
    if args and args[0] == "install":
        d.mkdir(parents=True, exist_ok=True)
        if len(list(d.glob("*.svg"))) > 500:
            info(f"Đã có {len(list(d.glob('*.svg')))} biểu tượng.")
            return 0
        try:
            ver = subprocess.run(["npm", "view", "lucide-static", "version"], capture_output=True, text=True, timeout=60).stdout.strip()
        except Exception:  # noqa: BLE001
            ver = ""
        ver = ver or "0.469.0"
        url = f"https://registry.npmjs.org/lucide-static/-/lucide-static-{ver}.tgz"
        tgz = RUNTIME / "lucide.tgz"
        urllib.request.urlretrieve(url, tgz)
        with tarfile.open(tgz) as t:
            for mem in t.getmembers():
                if mem.name.startswith("package/icons/") and mem.name.endswith(".svg"):
                    mem.name = Path(mem.name).name
                    t.extract(mem, d, filter="data")
        tgz.unlink()
        info(f"Đã cài {len(list(d.glob('*.svg')))} biểu tượng Lucide {ver} → {d}")
        return 0
    if args and args[0] == "find":
        words = [w.lower() for w in args[1:]]
        hits = [f.stem for f in sorted(d.glob("*.svg")) if all(w in f.stem for w in words)]
        info(", ".join(hits[:60]) or "Không có. Thử từ tiếng Anh: check, star, arrow-right, users, chart-bar, calendar, map-pin, phone…")
        return 0
    die(__doc__)


def main(cmd, args):
    if cmd == "font":
        if not args or args[0] != "get":
            die(__doc__)
        return font_get(args[1:])
    if cmd == "icons":
        return icons(args)
    if not args:
        die(__doc__)
    return {"find": find, "add": add, "list": list_, "scan": scan}.get(args[0], lambda a: die(__doc__))(args[1:])

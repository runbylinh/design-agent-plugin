"""Brand Kit: đọc brand.json (dùng chung với plugin video-edit), chuẩn hoá cho dựng ảnh, tạo CSS font + màu.

  ia brand show [<brand>]          tóm tắt Brand Kit đang dùng
  ia brand check [<brand>]         kiểm tra Brand Kit đủ để dựng ảnh chưa (màu, font có file, logo, guideline, mẫu)
  ia brand init <brand> [--tu <thư mục brand-kit có sẵn>]   tạo Brand Kit mới (hoặc nối Brand Kit của video-edit)
  ia brand colors <ảnh…>           lấy 6 màu chủ đạo từ logo / ảnh mẫu
"""
import re
import shutil
from collections import Counter
from pathlib import Path

from common import PLUGIN, RUNTIME, die, info, read_json, save_studio_config, slug, studio_config, warn, write_json

WEIGHTS = {"thin": 100, "extralight": 200, "light": 300, "regular": 400, "medium": 500, "semibold": 600,
           "bold": 700, "extrabold": 800, "black": 900}


def brand_dir(name=None, cfg=None):
    cfg = cfg or studio_config()
    kits = cfg.get("brand_kits", {})
    name = name or cfg.get("brand_mac_dinh")
    if not name:
        die("Studio chưa có brand mặc định. Chạy `ia brand init <brand>`.")
    if name not in kits:
        die(f"Studio chưa có Brand Kit '{name}'. Có: {', '.join(kits) or '(chưa có)'}.")
    d = Path(kits[name]).expanduser()
    if not d.is_absolute():
        d = Path(cfg["_dir"]) / d
    if not (d / "brand.json").exists():
        die(f"Thư mục Brand Kit {d} thiếu brand.json.")
    return name, d


def _font(spec, default_weight):
    if isinstance(spec, str):
        spec = {"family": spec}
    spec = dict(spec or {})
    spec.setdefault("family", "Be Vietnam Pro")
    spec.setdefault("weight", default_weight)
    return spec


def load(name=None, cfg=None):
    name, d = brand_dir(name, cfg)
    raw = read_json(d / "brand.json")
    c = dict(raw.get("colors", {}))
    c.setdefault("primary", "#111111")
    c.setdefault("secondary", c["primary"])
    c.setdefault("highlight", c.get("pink", c["primary"]))
    c.setdefault("dark", "#111111")
    c.setdefault("light", c.get("purple_light", "#F7F7F7"))
    c.setdefault("paper", "#FFFFFF")
    fonts = raw.get("fonts") or {}
    single = raw.get("font") or {}
    heading = _font(fonts.get("heading") or single, 800)
    body = _font(fonts.get("body") or {"family": heading["family"], "file": None}, 500)
    logos = raw.get("logos")
    if not logos and raw.get("logo"):
        lg = raw["logo"]
        logos = [lg if isinstance(lg, dict) else {"file": lg}]
    logos = [dict({"variant": "chinh", "nen": "sang"}, **lg) for lg in (logos or []) if lg.get("file")]
    img = raw.get("image", {})
    return {
        "key": name, "dir": str(d), "name": raw.get("name", name), "handle": raw.get("handle", ""),
        "colors": c, "fonts": {"heading": heading, "body": body}, "logos": logos,
        "radius": img.get("radius", 24), "spacing": img.get("spacing", 64),
        "style": img.get("style", ""), "photo_style": img.get("photo_style", ""),
        "rules": raw.get("rules", {"nen_lam": [], "khong_lam": []}),
        "guideline": (d / "brand.md").read_text(encoding="utf-8") if (d / "brand.md").exists() else "",
        "_raw": raw,
    }


def logo_file(brand, nen="sang"):
    """Logo hợp nền: nen = 'sang' (logo màu/đậm) hoặc 'toi' (logo trắng)."""
    pick = [lg for lg in brand["logos"] if lg.get("nen") == nen] or brand["logos"]
    for lg in pick:
        f = Path(brand["dir"]) / lg["file"]
        if f.exists():
            return f
    return None


# ------------------------------------------------------------------ font

def font_files(family, brand_dirs=()):
    """Tìm file font: Brand Kit/fonts → ~/.image-agent/fonts/<slug>. Trả {weight: Path}."""
    key = re.sub(r"[^a-z0-9]", "", family.lower())
    found = {}
    places = [Path(b) / "fonts" for b in brand_dirs] + [RUNTIME / "fonts" / slug(family)]
    for place in places:
        if not place.exists():
            continue
        for f in sorted(place.rglob("*")):
            if f.suffix.lower() not in (".ttf", ".otf", ".woff2", ".woff"):
                continue
            stem = f.stem.lower().replace(" ", "").replace("_", "-")
            if key not in re.sub(r"[^a-z0-9]", "", stem):
                continue
            if "italic" in stem:
                continue
            w = 400
            tail = stem.split("-")[-1]
            for nm, val in WEIGHTS.items():
                if tail == nm:
                    w = val
            found.setdefault(w, f)
    return found


def font_css(brand):
    css, missing = [], []
    for role in ("heading", "body"):
        spec = brand["fonts"][role]
        files = {}
        if spec.get("file"):
            f = Path(brand["dir"]) / spec["file"]
            if f.exists():
                files[int(spec.get("weight", 400))] = f
        files.update({w: f for w, f in font_files(spec["family"], [brand["dir"]]).items() if w not in files})
        if not files:
            missing.append(spec["family"])
        for w, f in sorted(files.items()):
            css.append(f"@font-face{{font-family:'{spec['family']}';font-weight:{w};src:url('{f.as_uri()}')}}")
    return "\n".join(dict.fromkeys(css)), sorted(set(missing))


# ------------------------------------------------------------------ lệnh

def cmd_show(name):
    b = load(name)
    info(f"Brand: {b['name']} ({b['key']})  ·  {b['dir']}")
    info("Màu: " + "  ".join(f"{k}={v}" for k, v in b["colors"].items()))
    for role in ("heading", "body"):
        f = b["fonts"][role]
        info(f"Font {role}: {f['family']} {f.get('weight', '')}")
    info(f"Logo: {', '.join(lg['file'] + ' (nền ' + lg['nen'] + ')' for lg in b['logos']) or 'CHƯA CÓ'}")
    info(f"Bo góc {b['radius']}px · lề {b['spacing']}px · phong cách: {b['style'] or '—'}")
    mau = sorted((Path(b["dir"]) / "mau").glob("*.json"))
    info(f"Mẫu đã duyệt: {len(mau)}" + (" — " + ", ".join(m.stem for m in mau[:10]) if mau else ""))
    rules = b["rules"]
    if rules.get("nen_lam") or rules.get("khong_lam"):
        info(f"Nên làm: {len(rules.get('nen_lam', []))} quy tắc · Không làm: {len(rules.get('khong_lam', []))} quy tắc")


def cmd_check(name):
    b = load(name)
    problems, notes = [], []
    for k in ("primary", "secondary", "highlight", "dark"):
        if not re.match(r"^#[0-9A-Fa-f]{6}$", b["colors"].get(k, "")):
            problems.append(f"màu '{k}' chưa có mã #RRGGBB")
    _, missing = font_css(b)
    for fam in missing:
        problems.append(f"font '{fam}' chưa có file — chạy `ia font get \"{fam}\"` (Google Fonts) hoặc chép file vào {b['dir']}/fonts/")
    if not b["logos"]:
        problems.append("chưa khai báo logo (brand.json → logos)")
    else:
        for lg in b["logos"]:
            if not (Path(b["dir"]) / lg["file"]).exists():
                problems.append(f"thiếu file logo {lg['file']}")
        if not any(lg.get("nen") == "toi" for lg in b["logos"]):
            notes.append("chưa có logo cho nền tối (nen: toi)")
    if len(b["guideline"]) < 200:
        problems.append("brand.md (guideline, tinh thần thương hiệu) còn trống/quá ngắn")
    if not b["rules"].get("khong_lam"):
        notes.append("chưa có danh sách 'không làm' (brand.json → rules.khong_lam)")
    mau = list((Path(b["dir"]) / "mau").glob("*.json"))
    refs = [f for f in (Path(b["dir"]) / "anh-mau").glob("*") if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")] \
        if (Path(b["dir"]) / "anh-mau").exists() else []
    if not mau and not refs:
        notes.append("chưa có mẫu đã duyệt (mau/) hay ảnh mẫu đúng chất (anh-mau/) — nên có 5–10")
    info(f"Brand Kit {b['key']}: " + ("✅ đủ để dựng ảnh" if not problems else f"❌ {len(problems)} vấn đề"))
    for p in problems:
        info(f"  ❌ {p}")
    for n in notes:
        info(f"  · {n}")
    return 0 if not problems else 1


def cmd_init(name, src=None):
    if slug(name) != name:
        die("Tên brand: chữ thường không dấu, nối bằng gạch ngang. Ví dụ: ngo-diu-spa")
    cfg = studio_config()
    kits = cfg.setdefault("brand_kits", {})
    if name in kits:
        die(f"Studio đã có Brand Kit '{name}' → {kits[name]}")
    if src:
        d = Path(src).expanduser().resolve()
        if not (d / "brand.json").exists():
            die(f"{d} không có brand.json.")
        info(f"Nối Brand Kit có sẵn (dùng chung với video-edit): {d}")
    else:
        d = Path(cfg["_dir"]) / "brand-kit" / name
        if d.exists():
            die(f"{d} đã tồn tại.")
        shutil.copytree(PLUGIN / "templates" / "brand-kit", d)
        bj = read_json(d / "brand.json")
        bj["name"] = name
        write_json(d / "brand.json", bj)
        info(f"Đã tạo {d} — điền brand.json + brand.md, chép logo vào logo/, font vào fonts/.")
    for sub in ("mau", "thanh-phan", "anh-mau"):
        (d / sub).mkdir(exist_ok=True)
    kits[name] = str(d)
    cfg.setdefault("brand_mac_dinh", name)
    save_studio_config(cfg)


def cmd_colors(images):
    from PIL import Image
    counts, sums = Counter(), {}
    for img in images:
        f = Path(img).expanduser()
        if not f.exists():
            die(f"Không thấy ảnh: {f}")
        im = Image.open(f).convert("RGBA").resize((96, 96))
        for r, g, b, a in im.getdata():
            if a < 128:
                continue
            mx, mn = max(r, g, b), min(r, g, b)
            if mx > 238 and mn > 230 or mx < 22:
                continue
            key = (r // 24, g // 24, b // 24)
            counts[key] += 1
            acc = sums.setdefault(key, [0, 0, 0])
            acc[0] += r; acc[1] += g; acc[2] += b
    total = sum(counts.values()) or 1
    info("Màu chủ đạo (đã bỏ nền trắng/đen):")
    for key, n in counts.most_common(6):
        r, g, b = (round(c / n) for c in sums[key])
        info(f"  #{r:02X}{g:02X}{b:02X}  {n / total * 100:4.0f}%")


def main(args):
    if not args:
        die(__doc__)
    act, rest = args[0], args[1:]
    if act == "show":
        cmd_show(rest[0] if rest else None)
    elif act == "check":
        return cmd_check(rest[0] if rest else None)
    elif act == "init":
        if not rest:
            die("ia brand init <brand> [--tu <thư mục>]")
        src = rest[rest.index("--tu") + 1] if "--tu" in rest else None
        cmd_init(rest[0], src)
    elif act == "colors":
        cmd_colors(rest)
    else:
        die(__doc__)
    return 0

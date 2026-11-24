"""Nghiên cứu mẫu thiết kế, bố cục riêng của brand, landing page.

  ia research new --ten "…" [--loai <loại ấn phẩm|landing>]   tạo phiên nghiên cứu RS-YYMMDD-NN
  ia research add <RS> <ảnh|thư mục…> --url <link> --nguon <nền tảng> [--ghi-chu "…"]
  ia research moodboard <RS> [--cot 4]                          ghép ảnh mẫu đánh số → moodboard.png
  ia research list · ia research show <RS>
  ia research done <RS> [--goi "<đã đóng gói gì>"]

  ia layout check <file.json>                                   kiểm cấu trúc bố cục
  ia layout save <file.json> --ten <tên> [--tu RS-…]            lưu vào Brand Kit/thanh-phan/layouts
  ia layout rm <tên>                                            xoá bố cục của brand (vd bản -thu bị loại)

  ia landing new --ten "…" [--muc-tieu dang-ky|ban-hang|su-kien|gioi-thieu]
  ia landing tokens [--brand x]                                 CSS màu/font của Brand Kit cho landing
  ia landing check <LP> [--v N]                                 chụp máy tính + điện thoại, kiểm lỗi
  ia landing version <LP> --note "…"                            phiên bản mới từ bản hiện tại
  ia landing approve <LP> --v N --xac-nhan "<lời người dùng>"   chép bản duyệt vào final/
  ia landing list
"""
import re
import shutil
from datetime import datetime
from pathlib import Path

from common import PLUGIN, die, find_studio, info, now, read_json, slug, warn, write_json

IMG_EXT = (".png", ".jpg", ".jpeg", ".webp")
RS_RE = re.compile(r"^RS-\d{6}-\d{2,3}$")
LP_RE = re.compile(r"^LP-\d{6}-\d{2,3}$")
MUC_TIEU = ("dang-ky", "ban-hang", "su-kien", "gioi-thieu")


def opt(args, name, default=None):
    if name in args:
        i = args.index(name)
        if i + 1 < len(args):
            return args[i + 1]
        die(f"Thiếu giá trị cho {name}")
    return default


def _new_id(root, prefix):
    day = datetime.now().strftime("%y%m%d")
    root.mkdir(parents=True, exist_ok=True)
    n = 1 + max([int(p.name.split("-")[-1]) for p in root.glob(f"{prefix}-{day}-*") if p.name.split("-")[-1].isdigit()] or [0])
    return f"{prefix}-{day}-{n:02d}"


def _dir(kind, rid):
    st = find_studio()
    rx, folder = (RS_RE, "research") if kind == "RS" else (LP_RE, "landing")
    if not rx.match(rid or ""):
        die(f"Mã '{rid}' không đúng dạng {kind}-YYMMDD-NN.")
    d = st / folder / rid
    if not d.exists():
        die(f"Không thấy {rid} trong {st / folder}. Xem `ia {folder} list`.")
    return d


# ================================================================== research

PHAN_TICH = """# {ten} — {rid}

Loại: {loai} · Bắt đầu: {luc}

## 1. Câu hỏi nghiên cứu
<Ấn phẩm gì, cho brand nào, mục đích gì; muốn học điều gì (bố cục mới, cách dùng ảnh, cách trình bày số liệu…)>

## 2. Nguồn đã xem
| # | Nền tảng | Link | Ngày xem | Vì sao chọn |
|---|---|---|---|---|

## 3. Phân tích từng mẫu
<Theo khung trong references/research-mau.md §3 — mỗi mẫu một khối ngắn>

## 4. Mẫu lặp lại & xu hướng
| Mẫu lặp | Thấy ở mẫu số | Đang nổi / Phổ biến / Bão hoà | Hợp brand? |
|---|---|---|---|

## 5. Đề xuất hướng áp dụng cho brand
<3–5 hướng, mỗi hướng: tên ngắn · học từ mẫu số … · dùng cho loại ấn phẩm nào · thay đổi gì so với bố cục đang có · rủi ro>

## 6. Đã đóng gói
<Bố cục mới, mẫu đã duyệt, quy tắc thêm vào brand.md — điền khi xong>
"""


def research(args):
    if not args:
        die(__doc__)
    act, rest = args[0], args[1:]
    st = find_studio()
    root = st / "research"
    if act == "new":
        ten = opt(rest, "--ten") or die("Thiếu --ten")
        loai = opt(rest, "--loai", "chung")
        rid = _new_id(root, "RS")
        d = root / rid
        (d / "mau").mkdir(parents=True)
        (d / "thu").mkdir()
        write_json(d / "research.json", {"id": rid, "ten": ten, "loai": loai, "luc": now(), "trang_thai": "Đang nghiên cứu",
                                         "mau": [], "goi": []})
        (d / "phan-tich.md").write_text(PHAN_TICH.format(ten=ten, rid=rid, loai=loai, luc=now()), encoding="utf-8")
        info(f"Đã tạo {d}\n  mau/ ảnh mẫu (ia research add) · phan-tich.md · thu/ ghi chú bản thử")
        info(rid)
        return 0
    if act == "list":
        rows = sorted(root.glob("RS-*/research.json")) if root.exists() else []
        if not rows:
            info("Chưa có phiên nghiên cứu nào.")
        for f in rows:
            r = read_json(f)
            info(f"{r['id']}  [{r.get('trang_thai')}]  {r['ten']}  · {r.get('loai')} · {len(r.get('mau', []))} mẫu · {r.get('luc')}")
        return 0
    rid = rest[0] if rest else die("Thiếu mã RS")
    d = _dir("RS", rid)
    meta = read_json(d / "research.json")
    if act == "add":
        url = opt(rest, "--url") or die("Thiếu --url (link gốc của mẫu — bắt buộc để ghi nguồn)")
        nguon = opt(rest, "--nguon") or die("Thiếu --nguon (Pinterest, Behance, Meta Ads Library, Fanpage…)")
        note = opt(rest, "--ghi-chu", "")
        skip = {url, nguon, note}
        files = []
        for a in rest[1:]:
            if a.startswith("--") or a in skip:
                continue
            p = Path(a).expanduser()
            if p.is_dir():
                files += sorted(f for f in p.iterdir() if f.suffix.lower() in IMG_EXT)
            elif p.exists() and p.suffix.lower() in IMG_EXT:
                files.append(p)
            else:
                die(f"Không thấy ảnh {p}")
        if not files:
            die("Chưa đưa ảnh nào.")
        for f in files:
            n = len(meta["mau"]) + 1
            dst = d / "mau" / f"{n:02d}-{slug(nguon)}{f.suffix.lower()}"
            shutil.copy2(f, dst)
            meta["mau"].append({"so": n, "file": dst.name, "url": url, "nguon": nguon, "ngay": now()[:10], "ghi_chu": note})
            info(f"  #{n:02d} {dst.name}  ← {nguon}")
        write_json(d / "research.json", meta)
        return 0
    if act == "moodboard":
        return _moodboard(d, meta, int(opt(rest, "--cot", 4)))
    if act == "show":
        info(f"{meta['id']} · {meta['ten']} · {meta.get('loai')} · {meta.get('trang_thai')}\n{d}")
        for m in meta["mau"]:
            info(f"  #{m['so']:02d} {m['nguon']:18s} {m['url']}  {m.get('ghi_chu', '')}")
        for g in meta.get("goi", []):
            info(f"  đóng gói: {g}")
        return 0
    if act == "done":
        meta["trang_thai"] = "Đã đóng gói"
        if opt(rest, "--goi"):
            meta["goi"].append(opt(rest, "--goi"))
        meta["xong"] = now()
        write_json(d / "research.json", meta)
        info(f"{rid} → Đã đóng gói.")
        return 0
    die(__doc__)


def _moodboard(d, meta, cols):
    from PIL import Image, ImageDraw, ImageFont
    items = [m for m in meta["mau"] if (d / "mau" / m["file"]).exists()]
    if not items:
        die("Chưa có ảnh mẫu (ia research add).")
    cell, pad, lab = 420, 24, 44
    cols = max(1, min(cols, len(items)))
    rows = (len(items) + cols - 1) // cols
    W = cols * cell + (cols + 1) * pad
    H = rows * (cell + lab) + (rows + 1) * pad
    board = Image.new("RGB", (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(board)
    font = None
    for cand in ("/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf",
                 "C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if Path(cand).exists():
            font = ImageFont.truetype(cand, 22)
            break
    font = font or ImageFont.load_default()
    for i, m in enumerate(items):
        r, c = divmod(i, cols)
        x = pad + c * (cell + pad)
        y = pad + r * (cell + lab + pad)
        im = Image.open(d / "mau" / m["file"]).convert("RGB")
        im.thumbnail((cell, cell))
        board.paste(im, (x + (cell - im.width) // 2, y + (cell - im.height) // 2))
        draw.rectangle([x, y, x + cell - 1, y + cell - 1], outline=(225, 225, 225))
        draw.text((x, y + cell + 10), f"#{m['so']:02d}  {m['nguon']}", fill=(40, 40, 40), font=font)
    out = d / "moodboard.png"
    board.save(out)
    info(f"Moodboard: {out}  ({len(items)} mẫu)")
    return 0


# ================================================================== layout

def layout_problems(lay):
    errs = []
    if not isinstance(lay, dict):
        return ["File không phải đối tượng JSON."]
    for k in ("mo_ta", "dung_cho", "variants"):
        if k not in lay:
            errs.append(f"Thiếu khoá '{k}'.")
    variants = lay.get("variants") or {}
    if not isinstance(variants, dict) or not variants:
        errs.append("'variants' phải có ít nhất một tỉ lệ (vd \"4:5\").")
        return errs
    for rk, v in variants.items():
        if not re.match(r"^\d+(\.\d+)?:\d+(\.\d+)?$", rk):
            errs.append(f"Tỉ lệ '{rk}' sai dạng (cần dạng 4:5, 16:9).")
        regions = (v or {}).get("regions") or {}
        if not regions:
            errs.append(f"[{rk}] chưa có vùng nào trong 'regions'.")
        for name, reg in regions.items():
            box = reg.get("box")
            if not (isinstance(box, list) and len(box) == 4 and all(isinstance(n, (int, float)) for n in box)):
                errs.append(f"[{rk}] vùng '{name}': box phải là [x, y, w, h].")
                continue
            x, y, w, h = box
            if min(box) < 0 or w <= 0 or h <= 0 or x + w > 1.001 or y + h > 1.001:
                errs.append(f"[{rk}] vùng '{name}': box {box} ra ngoài khung (dùng tỉ lệ 0–1).")
    return errs


def layout(args):
    if len(args) < 2 or args[0] not in ("check", "save", "rm"):
        die(__doc__)
    import brand as brandmod
    if args[0] == "rm":
        b = brandmod.load()
        f = Path(b["dir"]) / "thanh-phan" / "layouts" / f"{slug(args[1])}.json"
        if not f.exists():
            die(f"Brand {b['key']} không có bố cục '{args[1]}' (bố cục của plugin không xoá được).")
        f.unlink()
        info(f"Đã xoá bố cục '{f.stem}' khỏi Brand Kit {b['key']}.")
        return 0
    f = Path(args[1]).expanduser()
    lay = read_json(f)
    errs = layout_problems(lay)
    if errs:
        for e in errs:
            info(f"  ❌ {e}")
        die(f"Bố cục {f.name} chưa hợp lệ.", 2)
    if args[0] == "check":
        info(f"✅ {f.name} hợp lệ · tỉ lệ: {', '.join(lay['variants'])}")
        return 0
    ten = slug(opt(args, "--ten") or die("Thiếu --ten"))
    if (PLUGIN / "templates" / "layouts" / f"{ten}.json").exists():
        die(f"Tên '{ten}' trùng bố cục có sẵn của plugin — chọn tên khác.")
    b = brandmod.load()
    dst = Path(b["dir"]) / "thanh-phan" / "layouts" / f"{ten}.json"
    lay["name"] = ten
    if opt(args, "--tu"):
        lay["nguon_nghien_cuu"] = opt(args, "--tu")
    lay["luu_luc"] = now()
    write_json(dst, lay)
    info(f"Đã lưu bố cục '{ten}' vào Brand Kit {b['key']}: {dst}\nDùng: \"layout\": \"{ten}\" trong design.json · xem `ia layouts`.")
    rs = opt(args, "--tu")
    if rs and RS_RE.match(rs):
        d = find_studio() / "research" / rs
        if (d / "research.json").exists():
            meta = read_json(d / "research.json")
            meta.setdefault("goi", []).append(f"bố cục {ten}")
            write_json(d / "research.json", meta)
    return 0


# ================================================================== landing

STARTER = """<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{ten}</title>
<meta name="description" content="">
{font_link}
<style>
{tokens}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:var(--font-body);color:var(--c-text);background:var(--c-paper);line-height:1.6;font-size:17px}}
h1,h2,h3{{font-family:var(--font-heading);color:var(--c-dark);line-height:1.25}}
img{{max-width:100%;height:auto;display:block}}
.wrap{{max-width:1120px;margin:0 auto;padding:0 20px}}
section{{padding:88px 0}}
/* Viết tiếp theo references/landing-page.md */
</style>
</head>
<body>
<!-- Hero -->
<section class="hero"><div class="wrap">
  <h1>{ten}</h1>
</div></section>
</body>
</html>
"""


def _google_link(families):
    fams = [f for f in dict.fromkeys(families) if f]
    if not fams:
        return ""
    q = "&".join("family=" + f.replace(" ", "+") + ":wght@400;500;600;700;800;900" for f in fams)
    return f'<link rel="preconnect" href="https://fonts.googleapis.com">\n<link href="https://fonts.googleapis.com/css2?{q}&display=swap" rel="stylesheet">'


def brand_tokens(name=None):
    import brand as brandmod
    b = brandmod.load(name)
    c = b["colors"]
    lines = [":root{"]
    for k, v in c.items():
        # "text" trong brand.json là màu phụ đề video (thường trắng) — không dùng cho chữ trang web
        if isinstance(v, str) and v.startswith("#") and k != "text":
            lines.append(f"  --c-{slug(k)}:{v};")
    lines.append(f"  --c-text:{c.get('body_text', c['dark'])};")
    lines.append(f"  --font-heading:'{b['fonts']['heading']['family']}',system-ui,sans-serif;")
    lines.append(f"  --font-body:'{b['fonts']['body']['family']}',system-ui,sans-serif;")
    lines.append(f"  --radius:{min(int(b['radius']), 16)}px;")
    lines.append("}")
    return b, "\n".join(lines), _google_link([b["fonts"]["heading"]["family"], b["fonts"]["body"]["family"]])


CHECK_JS = r"""
() => {
  const vw = window.innerWidth, out = {};
  out.title = document.title || '';
  out.desc = (document.querySelector('meta[name=description]')||{}).content || '';
  out.viewport = !!document.querySelector('meta[name=viewport]');
  out.h1 = document.querySelectorAll('h1').length;
  out.scrollW = document.documentElement.scrollWidth;
  out.overflow = [];
  if (out.scrollW > vw + 1) {
    for (const el of document.body.querySelectorAll('*')) {
      const r = el.getBoundingClientRect();
      if (r.width && r.right > vw + 1 && getComputedStyle(el).position !== 'fixed') {
        out.overflow.push((el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).join('.') : '')).slice(0, 60) + ' rộng tới ' + Math.round(r.right) + 'px');
        if (out.overflow.length >= 5) break;
      }
    }
  }
  out.brokenImg = [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src')).slice(0, 10);
  out.noAlt = [...document.images].filter(i => !i.hasAttribute('alt')).length;
  out.extScripts = [...document.scripts].filter(s => s.src).map(s => s.src).slice(0, 5);
  out.details = document.querySelectorAll('details').length;
  out.anim = 0; out.small = 0; out.lowContrast = [];
  const rgb = s => { const m = s.match(/[\d.]+/g); return m ? m.map(Number) : null; };
  const lum = c => { const a = c.slice(0,3).map(v => { v /= 255; return v <= 0.03928 ? v/12.92 : Math.pow((v+0.055)/1.055, 2.4); }); return 0.2126*a[0]+0.7152*a[1]+0.0722*a[2]; };
  const bgOf = el => { for (let e = el; e; e = e.parentElement) { const cs = getComputedStyle(e);
      if (cs.backgroundImage && cs.backgroundImage !== 'none') return null;
      const c = rgb(cs.backgroundColor); if (c && (c.length < 4 || c[3] > 0.5)) return c; } return [255,255,255]; };
  for (const el of document.body.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.animationName && cs.animationName !== 'none') out.anim++;
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim().length > 1);
    if (!own) continue;
    const r = el.getBoundingClientRect();
    if (!r.width || !r.height || cs.visibility === 'hidden' || cs.display === 'none') continue;
    if (parseFloat(cs.fontSize) < 13) out.small++;
    if (cs.webkitBackgroundClip === 'text' || cs.backgroundClip === 'text') continue;
    const fg = rgb(cs.color), bg = bgOf(el);
    if (!fg || !bg) continue;
    const L1 = lum(fg), L2 = lum(bg), ratio = (Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05);
    const big = parseFloat(cs.fontSize) >= 24 || (parseFloat(cs.fontSize) >= 18.6 && parseInt(cs.fontWeight) >= 700);
    if (ratio < (big ? 3 : 4.5) && out.lowContrast.length < 8)
      out.lowContrast.push('"' + el.textContent.trim().slice(0, 40) + '" ' + ratio.toFixed(1) + ':1');
  }
  out.emptyLinks = [...document.querySelectorAll('a')].filter(a => { const h = (a.getAttribute('href')||'').trim(); return !h || h === '#'; })
      .map(a => a.textContent.trim().slice(0, 30)).slice(0, 8);
  out.height = document.documentElement.scrollHeight;
  return out;
}
"""


def _ver(d, v=None):
    meta = read_json(d / "landing.json")
    v = int(v or meta.get("phien_ban_hien_tai", 1))
    vd = d / f"v{v}"
    if not (vd / "index.html").exists():
        die(f"Không thấy {vd / 'index.html'}")
    return meta, v, vd


def landing_check(d, v=None):
    from playwright.sync_api import sync_playwright
    meta, v, vd = _ver(d, v)
    xem = vd / "xem"
    xem.mkdir(exist_ok=True)
    errors, warns, res = [], [], {}
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for name, vp in (("may-tinh", {"width": 1440, "height": 900}), ("dien-thoai", {"width": 390, "height": 844})):
            pg = br.new_page(viewport=vp, device_scale_factor=1 if name == "may-tinh" else 2)
            pg.goto((vd / "index.html").as_uri())
            try:
                pg.wait_for_load_state("networkidle", timeout=15000)
            except Exception:
                warns.append("Trang tải chưa xong sau 15 giây (font/ảnh ngoài chậm?).")
            pg.evaluate("document.fonts.ready")
            res[name] = pg.evaluate(CHECK_JS)
            pg.screenshot(path=str(xem / f"{name}-man-dau.png"))
            if res[name]["height"] <= 16000:
                pg.screenshot(path=str(xem / f"{name}.png"), full_page=True)
            else:
                warns.append(f"Trang dài {res[name]['height']}px — chỉ chụp màn đầu ({name}).")
            pg.close()
        br.close()
    m, pc = res["dien-thoai"], res["may-tinh"]
    if not m["viewport"]:
        errors.append("Thiếu <meta name=viewport> → điện thoại hiện trang thu nhỏ.")
    if m["overflow"] or m["scrollW"] > 391:
        errors.append(f"Điện thoại bị tràn ngang ({m['scrollW']}px > 390px): " + "; ".join(m["overflow"] or ["chưa rõ phần tử"]))
    if pc["brokenImg"]:
        errors.append("Ảnh không tải được: " + ", ".join(pc["brokenImg"]))
    if pc["h1"] != 1:
        errors.append(f"Trang cần đúng 1 thẻ <h1> (đang có {pc['h1']}).")
    if not pc["title"]:
        errors.append("Thiếu <title>.")
    if not pc["desc"]:
        warns.append("Thiếu meta description (xem trước khi chia sẻ link).")
    if pc["noAlt"]:
        warns.append(f"{pc['noAlt']} ảnh thiếu alt.")
    if pc["emptyLinks"]:
        warns.append("Nút/link chưa có đích (href trống hoặc #): " + ", ".join(pc["emptyLinks"]))
    if pc["extScripts"]:
        warns.append("Có script ngoài (" + ", ".join(pc["extScripts"]) + ") — LadiPage/HTML dán có thể chặn.")
    if pc["details"]:
        warns.append(f"Có {pc['details']} thẻ <details> — LadiPage hiện mũi tên tam giác xấu, nên làm thẻ hiện sẵn.")
    if pc["anim"]:
        warns.append(f"{pc['anim']} phần tử có animation — khi dán vào LadiPage chữ có thể bị mờ xám.")
    if m["small"]:
        warns.append(f"{m['small']} khối chữ dưới 13px trên điện thoại.")
    for name, r in (("máy tính", pc), ("điện thoại", m)):
        for lc in r["lowContrast"]:
            warns.append(f"Tương phản thấp ({name}): {lc}")
    qa = {"phien_ban": v, "luc": now(), "loi": errors, "canh_bao": list(dict.fromkeys(warns)),
          "do_cao": {"may_tinh": pc["height"], "dien_thoai": m["height"]}}
    write_json(vd / "qa.json", qa)
    meta["trang_thai"] = "Chờ duyệt" if not errors else "Đang làm"
    write_json(d / "landing.json", meta)
    info(f"Kiểm {d.name} v{v}: {len(errors)} lỗi · {len(qa['canh_bao'])} cảnh báo")
    for e in errors:
        info(f"  ❌ {e}")
    for w in qa["canh_bao"]:
        info(f"  ⚠️ {w}")
    info(f"Ảnh xem: {xem}/ (may-tinh.png, dien-thoai.png, *-man-dau.png) — mở ra xem trước khi trình.")
    return 2 if errors else 0


def landing(args):
    if not args:
        die(__doc__)
    act, rest = args[0], args[1:]
    st = find_studio()
    root = st / "landing"
    if act == "tokens":
        _, tokens, link = brand_tokens(opt(rest, "--brand"))
        info(link + "\n<style>\n" + tokens + "\n</style>")
        return 0
    if act == "new":
        ten = opt(rest, "--ten") or die("Thiếu --ten")
        mt = opt(rest, "--muc-tieu", "dang-ky")
        if mt not in MUC_TIEU:
            die(f"--muc-tieu chỉ nhận: {', '.join(MUC_TIEU)}")
        b, tokens, link = brand_tokens(opt(rest, "--brand"))
        lid = _new_id(root, "LP")
        d = root / lid
        (d / "v1" / "assets").mkdir(parents=True)
        (d / "v1" / "index.html").write_text(STARTER.format(ten=ten, tokens=tokens, font_link=link), encoding="utf-8")
        (d / "brief.md").write_text(f"# {ten} — {lid}\n\nMục tiêu: {mt}\nBrand: {b['key']}\n\n"
                                    "## Khách xem là ai\n\n## Lời hứa chính\n\n## Offer / giá / hạn\n\n"
                                    "## Bằng chứng có thật (số liệu, feedback, logo đối tác)\n\n## CTA + đích của nút (link form, Zalo, hotline)\n\n"
                                    "## Nội dung gốc người dùng đưa\n", encoding="utf-8")
        write_json(d / "landing.json", {"id": lid, "ten": ten, "muc_tieu": mt, "brand": b["key"], "luc": now(),
                                        "trang_thai": "Mới", "phien_ban_hien_tai": 1, "phien_ban": [{"v": 1, "luc": now(), "note": "bản đầu"}]})
        info(f"Đã tạo {d}\n  brief.md · v1/index.html (đã có màu, font Brand Kit) · v1/assets/")
        info(lid)
        return 0
    if act == "list":
        rows = sorted(root.glob("LP-*/landing.json")) if root.exists() else []
        if not rows:
            info("Chưa có landing page nào.")
        for f in rows:
            r = read_json(f)
            info(f"{r['id']}  [{r.get('trang_thai')}]  {r['ten']} · {r.get('muc_tieu')} · v{r.get('phien_ban_hien_tai')} · {r.get('luc')}")
        return 0
    lid = rest[0] if rest else die("Thiếu mã LP")
    d = _dir("LP", lid)
    if act == "check":
        return landing_check(d, opt(rest, "--v"))
    if act == "version":
        meta, v, vd = _ver(d)
        nv = v + 1
        shutil.copytree(vd, d / f"v{nv}", ignore=shutil.ignore_patterns("xem", "qa.json"))
        meta["phien_ban_hien_tai"] = nv
        meta["trang_thai"] = "Đang làm"
        meta["phien_ban"].append({"v": nv, "luc": now(), "tu": v, "note": opt(rest, "--note", "")})
        write_json(d / "landing.json", meta)
        info(f"Đã tạo v{nv} từ v{v}: {d / f'v{nv}'}")
        return 0
    if act == "approve":
        xn = opt(rest, "--xac-nhan") or die("Thiếu --xac-nhan (nguyên văn lời người dùng đồng ý).", 2)
        meta, v, vd = _ver(d, opt(rest, "--v"))
        qa = read_json(vd / "qa.json", {})
        if not qa:
            die(f"v{v} chưa chạy `ia landing check`.", 2)
        if qa.get("loi"):
            die(f"v{v} còn {len(qa['loi'])} lỗi chặn — sửa rồi kiểm lại.", 2)
        fin = d / "final"
        if fin.exists():
            shutil.rmtree(fin)
        shutil.copytree(vd, fin, ignore=shutil.ignore_patterns("qa.json"))
        meta.update({"trang_thai": "Đã duyệt", "ban_duyet": {"v": v, "luc": now(), "xac_nhan": xn}})
        write_json(d / "landing.json", meta)
        info(f"Đã duyệt v{v} → {fin / 'index.html'}")
        return 0
    die(__doc__)


def main(cmd, args):
    if cmd == "research":
        return research(args)
    if cmd == "layout":
        return layout(args)
    if cmd == "landing":
        return landing(args)
    die(__doc__)

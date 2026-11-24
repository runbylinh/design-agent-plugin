"""Dựng một phiên bản: design.json → index.html → PNG từng trang + ảnh xem nhanh + kiểm tra tự động (QA lần 1, phần máy làm).

  ia render <DS-ID> [--v N]          dựng phiên bản N (mặc định: phiên bản hiện tại)
  ia render --file design.json --out <thư mục>   dựng thử ngoài job (không ghi manifest)

Kết quả trong jobs/<DS>/vN/:
  out/<trang>.png       ảnh đúng kích thước
  xem-nhanh.png         ghép các trang (carousel) để xem cả bộ
  xem-dien-thoai.png    thu nhỏ như khi lướt trên điện thoại — dùng để kiểm độ dễ đọc
  qa.json               lỗi chặn / cảnh báo máy kiểm được (chữ tràn, font thay thế, vùng an toàn, tương phản, chữ khoá bị đổi…)
"""
import json
from pathlib import Path

import brand as brandmod
from common import die, info, log, manifest, norm_text, read_json, save_manifest, text_hash, version_dir, warn, write_json
from compose import compose

FIT_JS = """
() => {
  const res = [];
  for (const el of document.querySelectorAll('.fit')) {
    const host = el.closest('.el');
    let size = parseFloat(getComputedStyle(el).fontSize);
    const start = size;
    const min = parseFloat(el.dataset.min || 14);
    const maxLines = parseInt(el.dataset.lines || 0);
    const lh = () => parseFloat(getComputedStyle(el).lineHeight) || size * 1.2;
    const avail = () => host.clientHeight - parseFloat(getComputedStyle(host).paddingTop) - parseFloat(getComputedStyle(host).paddingBottom);
    const tooTall = () => el.scrollHeight > avail() + 2 || el.scrollWidth > el.clientWidth + 2;
    const tooMany = () => maxLines > 0 && Math.round(el.scrollHeight / lh()) > maxLines;
    while ((tooTall() || tooMany()) && size > min) { size -= Math.max(1, size * 0.04); el.style.fontSize = size + 'px'; }
    res.push({id: host.dataset.id, page: host.closest('.page').id, start, size, overflow: tooTall(), lines: Math.round(el.scrollHeight / lh()), maxLines});
  }
  return res;
}
"""

BOXES_JS = """
() => [...document.querySelectorAll('.el')].map(e => {
  const p = e.closest('.page'); const pr = p.getBoundingClientRect(); const r = e.getBoundingClientRect();
  const t = e.querySelector('.txt');
  let ink = null, fs = null, weight = null, text = null, tr = null;
  if (t) {
    const cs = getComputedStyle(t); ink = cs.color; fs = parseFloat(cs.fontSize); weight = cs.fontWeight; text = t.innerText;
    const rg = document.createRange(); rg.selectNodeContents(t);
    tr = [...rg.getClientRects()].filter(b => b.width > 2 && b.height > 2).map(b => [b.left - pr.left, b.top - pr.top, b.width, b.height]);
  }
  return {id: e.dataset.id, type: e.dataset.type, role: e.dataset.role, locked: e.dataset.locked === '1', source: e.dataset.source,
          page: p.id, x: r.left - pr.left, y: r.top - pr.top, w: r.width, h: r.height, ink, fs, weight, text, tr};
})
"""

FONTS_JS = """
async (fams) => {
  await document.fonts.ready;
  const out = [];
  for (const f of fams) {
    const faces = await document.fonts.load(`700 40px '${f}'`, 'Ắệờ');
    out.push([f, faces.length > 0 && faces.every(x => x.status === 'loaded')]);
  }
  return out;
}
"""

MARKS_JS = """
() => [...document.querySelectorAll('mark')].map(mk => {
  const p = mk.closest('.page'); const pr = p.getBoundingClientRect(); const r = mk.getBoundingClientRect();
  const cs = getComputedStyle(mk); const host = mk.closest('.el');
  return {id: host.dataset.id + ' (chữ nhấn)', type: 'mark', role: '', page: p.id, x: r.left - pr.left, y: r.top - pr.top,
          w: r.width, h: r.height, ink: cs.color, fs: parseFloat(cs.fontSize), boxed: mk.classList.contains('m-box')};
})
"""

HIDE_TEXT_CSS = (".txt,.txt *,.chrome{color:transparent!important;-webkit-text-stroke-color:transparent!important;"
                 "text-shadow:none!important}")

MOBILE_WIDTH = {"16:9": 360, "4:5": 390, "1:1": 390, "9:16": 390}


def _rgb(css):
    import re
    nums = [float(x) for x in re.findall(r"[\d.]+", css or "")][:3]
    return tuple(int(v) for v in nums) if len(nums) == 3 else (0, 0, 0)


def _lum(rgb):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = rgb
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def _overlap(a, b):
    x = max(0, min(a[0] + a[2], b[0] + b[2]) - max(a[0], b[0]))
    y = max(0, min(a[1] + a[3], b[1] + b[3]) - max(a[1], b[1]))
    return x * y


def render_design(design, b, job, out_dir, locked_ref=None, keep_bare=False):
    """Dựng + kiểm. Trả (qa, files)."""
    from PIL import Image
    from playwright.sync_api import sync_playwright
    import presets

    doc, cv, pages, missing = compose(design, b, job)
    out_dir = Path(out_dir)
    (out_dir / "out").mkdir(parents=True, exist_ok=True)
    for old in (out_dir / "out").glob("*.png"):
        old.unlink()
    html_file = out_dir / "index.html"
    html_file.write_text(doc, encoding="utf-8")
    errors, warns = [], []
    for fam in missing:
        errors.append(f"Font '{fam}' không có file → trình duyệt dùng font thay thế. Chạy `ia font get \"{fam}\"` hoặc chép file font vào Brand Kit.")
    transparent = any(isinstance(p.get("bg", design.get("bg")), dict) and p.get("bg", design.get("bg")).get("transparent") for p in pages)
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={"width": cv["w"], "height": cv["h"]}, device_scale_factor=1)
        pg.goto(html_file.as_uri())
        pg.wait_for_load_state("networkidle")
        fams = sorted({b["fonts"]["heading"]["family"], b["fonts"]["body"]["family"]})
        for fam, ok in pg.evaluate(FONTS_JS, fams):
            if not ok and fam not in missing:
                errors.append(f"Font '{fam}' chưa tải được trước khi chụp (có thể thiếu đậm/nhạt) → chữ có thể bị thay font.")
        fits = pg.evaluate(FIT_JS)
        boxes = pg.evaluate(BOXES_JS) + [mk for mk in pg.evaluate(MARKS_JS) if not mk["boxed"]]
        files = []
        for p in pages:
            f = out_dir / "out" / f"{p['id']}.png"
            pg.locator(f"#{p['id']}").screenshot(path=str(f), omit_background=transparent)
            files.append(f)
        # ảnh nền không chữ để đo tương phản
        pg.add_style_tag(content=HIDE_TEXT_CSS)
        bare = {}
        for p in pages:
            f = out_dir / f".nen-{p['id']}.png"
            pg.locator(f"#{p['id']}").screenshot(path=str(f))
            bare[p["id"]] = f
        br.close()

    for f in fits:
        if f["overflow"]:
            errors.append(f"[{f['page']}] '{f['id']}': chữ vẫn tràn khung dù đã thu nhỏ tới {f['size']:.0f}px → rút gọn chữ hoặc nới khung.")
        elif f["size"] < f["start"] * 0.7:
            warns.append(f"[{f['page']}] '{f['id']}': phải thu nhỏ chữ {f['start']:.0f}→{f['size']:.0f}px để vừa — cân nhắc bớt chữ.")
        if f["maxLines"] and f["lines"] > f["maxLines"]:
            errors.append(f"[{f['page']}] '{f['id']}': {f['lines']} dòng, vượt giới hạn {f['maxLines']} dòng.")

    W, H = cv["w"], cv["h"]
    sx, sy, sw, sh = (cv["safe"][0] * W, cv["safe"][1] * H, cv["safe"][2] * W, cv["safe"][3] * H)
    rk = presets.ratio_key(W, H)
    mobile_scale = MOBILE_WIDTH.get(rk, 390) / W
    for bx in boxes:
        r = (bx["x"], bx["y"], bx["w"], bx["h"])
        important = bx["type"] in ("text", "list", "button", "logo") or bx["role"] in ("cta", "hook", "price")
        if bx["type"] == "mark":
            important = False
        if bx["x"] < -1 or bx["y"] < -1 or bx["x"] + bx["w"] > W + 1 or bx["y"] + bx["h"] > H + 1:
            if important:
                errors.append(f"[{bx['page']}] '{bx['id']}' nằm ra ngoài khung ảnh.")
        if important:
            if r[0] < sx - 2 or r[1] < sy - 2 or r[0] + r[2] > sx + sw + 2 or r[1] + r[3] > sy + sh + 2:
                warns.append(f"[{bx['page']}] '{bx['id']}' ra ngoài vùng an toàn của khổ này.")
            for name, a in (cv.get("avoid") or {}).items():
                ar = (a[0] * W, a[1] * H, a[2] * W, a[3] * H)
                if _overlap(r, ar) > 0.05 * r[2] * r[3]:
                    errors.append(f"[{bx['page']}] '{bx['id']}' đè lên vùng bị che: {name}.")
        if bx["type"] in ("text", "list", "button", "mark") and bx["fs"]:
            eff = bx["fs"] * mobile_scale
            if eff < 9.5:
                warns.append(f"[{bx['page']}] '{bx['id']}': chữ {bx['fs']:.0f}px chỉ còn ~{eff:.0f}px khi xem trên điện thoại — khó đọc.")
            if bx["ink"] and bx["type"] != "button":
                im = Image.open(bare[bx["page"]]).convert("RGB")
                px = []
                for q in (bx.get("tr") or [r]):
                    crop = im.crop((max(0, int(q[0])), max(0, int(q[1])), min(W, int(q[0] + q[2])), min(H, int(q[1] + q[3]))))
                    if crop.width > 2 and crop.height > 2:
                        px += list(crop.resize((24, 12)).getdata())
                if px:
                    px = sorted(px, key=_lum)
                    ink = _rgb(bx["ink"])
                    worst = min(contrast(ink, px[len(px) // 10]), contrast(ink, px[len(px) * 9 // 10]))
                    need = 3.0 if bx["fs"] >= 40 else 4.5
                    if worst < need:
                        (errors if worst < 2.2 else warns).append(
                            f"[{bx['page']}] '{bx['id']}': tương phản chữ/nền thấp ({worst:.1f}:1, cần ≥{need}:1) → đổi màu chữ, thêm nền/lớp tối.")
        if bx["type"] == "chart" and not bx.get("source"):
            errors.append(f"[{bx['page']}] biểu đồ '{bx['id']}' chưa ghi nguồn số liệu.")

    # chữ bị khoá: so với bản đã khoá
    locked_now = {}
    for p in pages:
        for el in p.get("elements", []):
            if el.get("content_locked"):
                val = el.get("content") if "content" in el else "\n".join(el.get("items", []))
                locked_now[el["id"]] = text_hash(val)
    if locked_ref:
        for k, hv in locked_ref.items():
            if k not in locked_now:
                errors.append(f"Thành phần khoá nội dung '{k}' đã bị xoá khỏi thiết kế.")
            elif locked_now[k] != hv:
                errors.append(f"Nội dung khoá '{k}' đã bị đổi chữ (chỉ được xuống dòng / tô nhấn).")

    for f in bare.values():
        if not keep_bare:
            f.unlink(missing_ok=True)
    # xem nhanh + xem trên điện thoại
    thumbs = [Image.open(f) for f in files]
    cols = min(len(thumbs), 5)
    rows = (len(thumbs) + cols - 1) // cols
    tw = 360
    th = round(tw * H / W)
    sheet = Image.new("RGB", (cols * tw + (cols + 1) * 12, rows * th + (rows + 1) * 12), (60, 60, 60))
    for i, im in enumerate(thumbs):
        sheet.paste(im.convert("RGB").resize((tw, th)), (12 + (i % cols) * (tw + 12), 12 + (i // cols) * (th + 12)))
    sheet.save(out_dir / "xem-nhanh.png")
    mw = round(W * mobile_scale)
    thumbs[0].convert("RGB").resize((mw, round(H * mobile_scale))).save(out_dir / "xem-dien-thoai.png")

    qa = {"loi": errors, "canh_bao": warns, "trang": [p["id"] for p in pages], "kich_thuoc": f"{W}x{H}",
          "noi_dung_khoa": locked_now, "chu": [{k: f[k] for k in ("page", "id", "size", "lines")} for f in fits]}
    write_json(out_dir / "qa.json", qa)
    return qa, files


def report(qa, files, out_dir):
    info(f"Đã dựng {len(files)} trang {qa['kich_thuoc']} → {out_dir}/out/")
    info(f"Xem cả bộ: {out_dir}/xem-nhanh.png · xem như trên điện thoại: {out_dir}/xem-dien-thoai.png")
    for e in qa["loi"]:
        info(f"  ❌ {e}")
    for w in qa["canh_bao"]:
        info(f"  ⚠️ {w}")
    if not qa["loi"] and not qa["canh_bao"]:
        info("  ✅ Máy kiểm không thấy lỗi — vẫn cần MỞ ẢNH ra xem (QA lần 1 bằng mắt).")


def main(args):
    if "--file" in args:
        design = read_json(args[args.index("--file") + 1])
        out = Path(args[args.index("--out") + 1]) if "--out" in args else Path("render-thu")
        b = brandmod.load(design.get("brand"))
        qa, files = render_design(design, b, Path(args[args.index("--file") + 1]).parent, out)
        report(qa, files, out)
        return 1 if qa["loi"] else 0
    if not args:
        die(__doc__)
    m = manifest(args[0])
    v = int(args[args.index("--v") + 1]) if "--v" in args else m.get("phien_ban_hien_tai", 1)
    vd = version_dir(m, v)
    # một phiên bản có thể chứa 2–3 hướng thiết kế: vN/huong-a/design.json, vN/huong-b/design.json…
    targets = [vd] if (vd / "design.json").exists() else sorted(p for p in vd.glob("huong-*") if (p / "design.json").exists())
    if "--huong" in args:
        targets = [vd / f"huong-{args[args.index('--huong') + 1]}"]
    if not targets:
        die(f"Không thấy design.json trong {vd} (hoặc {vd}/huong-*/).")
    locked_ref = m.get("noi_dung_khoa") or None
    total_err, total_warn = 0, 0
    for tdir in targets:
        design = read_json(tdir / "design.json")
        b = brandmod.load(design.get("brand") or m.get("brand"))
        qa, files = render_design(design, b, m["_dir"], tdir, locked_ref)
        if not locked_ref and qa["noi_dung_khoa"]:
            m["noi_dung_khoa"] = locked_ref = qa["noi_dung_khoa"]   # lần dựng đầu: ghi nhận chữ khoá làm mốc
        if len(targets) > 1:
            info(f"\n── {tdir.name}")
        report(qa, files, tdir)
        total_err += len(qa["loi"])
        total_warn += len(qa["canh_bao"])
    if len(targets) > 1:
        from PIL import Image
        sheets = [Image.open(t / "xem-nhanh.png") for t in targets]
        w = max(s.width for s in sheets)
        combo = Image.new("RGB", (w, sum(s.height for s in sheets)), (60, 60, 60))
        y = 0
        for s in sheets:
            combo.paste(s, (0, y))
            y += s.height
        combo.save(vd / "so-sanh-huong.png")
        info(f"\nSo sánh {len(targets)} hướng: {vd}/so-sanh-huong.png")
    ver = next((x for x in m["phien_ban"] if x["v"] == v), None)
    if ver:
        ver["trang_thai"] = "Đã dựng" if not total_err else "Có lỗi"
        ver["qa_may"] = {"loi": total_err, "canh_bao": total_warn}
        if len(targets) > 1:
            ver["huong"] = [t.name.replace("huong-", "") for t in targets]
    m["trang_thai"] = "Chờ duyệt" if not total_err else "Đang làm"
    log(m, f"dựng v{v}{' (' + str(len(targets)) + ' hướng)' if len(targets) > 1 else ''}: {total_err} lỗi, {total_warn} cảnh báo")
    save_manifest(m)
    import tracker
    note = (ver or {}).get("ghi_chu", "")
    tracker.upsert("Viec", m["design_id"], {"Trạng thái": m["trang_thai"], "Bản đang làm": f"v{v}"})
    tracker.recap(m["design_id"], v, "Dựng",
                  f"Dựng v{v}" + (f" — {len(targets)} hướng ({', '.join(t.name.replace('huong-', '').upper() for t in targets)})" if len(targets) > 1 else "")
                  + (f" · {note}" if note and note != "bản đầu" else ""),
                  qa_may=f"{total_err} lỗi, {total_warn} cảnh báo")
    tracker.hint_push()
    return 1 if total_err else 0

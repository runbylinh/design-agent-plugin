"""Xuất PPTX có chữ sửa được (để mở / nhập vào Canva, PowerPoint, Google Slides).

  ia pptx <DS> [--v N] [--huong a] [--out <file.pptx>]

Mỗi trang = một slide: ảnh nền (mọi thứ trừ chữ) + từng khối chữ là hộp chữ thật, giữ vị trí, cỡ, màu, đậm, căn lề.
Canva chỉ nhận font thường/đậm → độ đậm ≥ 600 thành Bold. Ảnh người/logo/khối màu nằm trong ảnh nền (không tách lớp).
Tải lên Canva: giao diện Canva → Tải lên → chọn file .pptx (Claude in Chrome: file_upload vào ô tải lên) → Canva tự tạo thiết kế.
"""
from pathlib import Path

from common import die, info, manifest, read_json, version_dir, warn

RUNS_JS = r"""
(pid) => {
  const page = document.getElementById(pid); const pr = page.getBoundingClientRect();
  const blocks = [];
  const isBlock = el => ['block', 'list-item', 'flex', 'grid', 'table', 'table-row'].includes(getComputedStyle(el).display);
  const own = e => [...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
  const targets = [...page.querySelectorAll('.txt')].filter(t => !(t.parentElement && t.parentElement.closest('.txt')))
      .concat([...page.querySelectorAll('.chrome *')].filter(own));
  for (const t of targets) {
    const r = t.getBoundingClientRect(); if (r.width < 2 || r.height < 2) continue;
    const runs = [];
    const walk = (node) => {
      for (const n of node.childNodes) {
        if (n.nodeType === 3) {
          const s = n.textContent.replace(/\s+/g, ' ');
          if (!s.trim()) { const last = runs[runs.length - 1]; if (last && !last.br && !/ $/.test(last.t)) last.t += ' '; continue; }
          const cs = getComputedStyle(n.parentElement);
          runs.push({t: s, color: cs.color, w: parseInt(cs.fontWeight) || 400, fs: parseFloat(cs.fontSize), fam: cs.fontFamily,
                     up: cs.textTransform === 'uppercase', it: cs.fontStyle === 'italic'});
        } else if (n.nodeType === 1) {
          if (n.tagName === 'BR') { if (runs.length && !runs[runs.length - 1].br) runs.push({br: true}); continue; }
          if (targets.includes(n)) continue;
          const blk = isBlock(n) && runs.length && !runs[runs.length - 1].br;
          if (blk) runs.push({br: true});
          walk(n);
        }
      }
    };
    walk(t);
    if (!runs.some(x => x.t && x.t.trim())) continue;
    const cs = getComputedStyle(t);
    blocks.push({x: r.left - pr.left, y: r.top - pr.top, w: r.width, h: r.height, align: cs.textAlign,
                 lh: parseFloat(cs.lineHeight) / parseFloat(cs.fontSize) || 1.2, runs});
  }
  return blocks;
}
"""


def _rgb(css):
    import re
    nums = [float(v) for v in re.findall(r"[\d.]+", css or "")][:4]
    if len(nums) < 3:
        return (0, 0, 0), 1.0
    return tuple(int(v) for v in nums[:3]), (nums[3] if len(nums) > 3 else 1.0)


def build(vd, out_file, design=None):
    """vd = thư mục phiên bản đã dựng (có index.html + .nen-<trang>.png)."""
    from playwright.sync_api import sync_playwright
    from pptx import Presentation
    from pptx.dml.color import RGBColor
    from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
    from pptx.util import Emu, Pt
    import compose

    vd = Path(vd)
    design = design or read_json(vd / "design.json")
    cv = compose.canvas_of(design)
    pages = compose.pages_of(design)
    W, H = cv["w"], cv["h"]
    scale = min(1.0, 5000 / max(W, H))  # PPTX tối đa 56 inch
    emu = lambda px: Emu(int(round(px * scale * 9525)))
    prs = Presentation()
    prs.slide_width, prs.slide_height = emu(W), emu(H)
    blank = prs.slide_layouts[6]
    aligns = {"center": PP_ALIGN.CENTER, "right": PP_ALIGN.RIGHT, "end": PP_ALIGN.RIGHT, "justify": PP_ALIGN.JUSTIFY}
    n_text = 0
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        pg.goto((vd / "index.html").as_uri())
        pg.wait_for_load_state("networkidle")
        pg.evaluate("document.fonts.ready")
        for p in pages:
            nen = vd / f".nen-{p['id']}.png"
            if not nen.exists():
                die(f"Thiếu ảnh nền không chữ {nen.name} — chạy `ia render` phiên bản này trước.")
            sl = prs.slides.add_slide(blank)
            sl.shapes.add_picture(str(nen), 0, 0, prs.slide_width, prs.slide_height)
            for b in pg.evaluate(RUNS_JS, p["id"]):
                pad = max(4, b["w"] * 0.03)
                tb = sl.shapes.add_textbox(emu(b["x"] - pad / 2), emu(b["y"]), emu(b["w"] + pad), emu(b["h"]))
                tf = tb.text_frame
                tf.word_wrap = True
                tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
                tf.vertical_anchor = MSO_ANCHOR.TOP
                para = tf.paragraphs[0]
                first = True
                for r in b["runs"]:
                    if r.get("br"):
                        para = tf.add_paragraph()
                        first = True
                        continue
                    text = r["t"].upper() if r.get("up") else r["t"]
                    if first:
                        text = text.lstrip()
                        para.alignment = aligns.get(b["align"], PP_ALIGN.LEFT)
                        para.line_spacing = round(min(max(b["lh"], 0.8), 2.0), 2)
                        first = False
                    if not text:
                        continue
                    run = para.add_run()
                    run.text = text
                    f = run.font
                    f.size = Pt(max(1, r["fs"] * 0.75 * scale))
                    f.bold = r["w"] >= 600
                    f.italic = bool(r.get("it"))
                    fam = (r.get("fam") or "").split(",")[0].strip().strip("'\"")
                    if fam:
                        f.name = fam
                    (cr, cg, cb), alpha = _rgb(r["color"])
                    if alpha < 0.05:
                        warn(f"[{p['id']}] chữ trong suốt / tô gradient '{text[:20]}' → đặt màu đen trong PPTX, chỉnh lại trên Canva.")
                        cr = cg = cb = 0
                    f.color.rgb = RGBColor(cr, cg, cb)
                n_text += 1
        br.close()
    for p in pages:
        (vd / f".nen-{p['id']}.png").unlink(missing_ok=True)
    out_file = Path(out_file)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    prs.save(out_file)
    return n_text, len(pages)


def main(args):
    if not args:
        die(__doc__)
    import brand as brandmod
    from render import render_design

    def opt(name, default=None):
        return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else default

    m = manifest(args[0])
    v = opt("--v") or (m.get("ban_duyet") or {}).get("v") or m.get("phien_ban_hien_tai")
    huong = opt("--huong") or ((m.get("ban_duyet") or {}).get("huong") if not opt("--v") else None)
    vd = version_dir(m, v) / (f"huong-{huong}" if huong else "")
    design = read_json(vd / "design.json")
    b = brandmod.load(design.get("brand") or m.get("brand"))
    render_design(design, b, m["_dir"], vd, m.get("noi_dung_khoa") or None, keep_bare=True)
    out = Path(opt("--out") or (Path(m["_dir"]) / ("approved" if m.get("ban_duyet") and not opt("--v") else f"v{v}") / f"{m['design_id']}.pptx"))
    n, pages = build(vd, out, design)
    info(f"PPTX: {out}  ({pages} trang, {n} khối chữ sửa được)")
    info("Canva: Tải lên → chọn file .pptx → Canva tạo thiết kế; nếu font hiện sai, chọn khối chữ → đổi font → 'Thay đổi tất cả'.")
    if not m.get("ban_duyet"):
        warn("Job chưa duyệt — đây là bản thử.")
    return 0

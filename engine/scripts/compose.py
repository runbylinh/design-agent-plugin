"""design.json → HTML. Mỗi trang (page) là một <section> đúng kích thước khung; mỗi thành phần đặt tuyệt đối.

Vị trí thành phần: element.box (px hoặc tỉ lệ 0–1) > vùng `slot` (mặc định = role) trong bố cục (layout) của trang.
Bố cục là "họ" có biến thể theo tỉ lệ khung (16:9, 4:5, 1:1, 9:16…) → đổi kích thước = dựng lại theo biến thể mới,
không kéo giãn. Xem references/design-json.md.
"""
import html
import re
from pathlib import Path

import chart as chartmod
import presets
from brand import font_css, logo_file
from common import PLUGIN, RUNTIME, die, read_json

LAYOUT_DIR = PLUGIN / "templates" / "layouts"
SIZES = {"xs": 0.026, "sm": 0.034, "md": 0.045, "lg": 0.06, "xl": 0.085, "xxl": 0.115, "mega": 0.16}


# ------------------------------------------------------------------ đọc design

def canvas_of(design):
    cv = dict(design.get("canvas") or {})
    if cv.get("preset"):
        try:
            p = presets.get(cv["preset"])
        except KeyError:
            die(f"Không có khổ '{cv['preset']}'. Xem `ia presets`.")
        cv.setdefault("w", p["w"])
        cv.setdefault("h", p["h"])
        cv.setdefault("safe", p.get("safe"))
        cv.setdefault("avoid", p.get("avoid", {}))
    if not cv.get("w") or not cv.get("h"):
        die("design.json thiếu canvas.preset hoặc canvas.w/h.")
    cv.setdefault("safe", [0.05, 0.05, 0.9, 0.9])
    cv.setdefault("avoid", {})
    return cv


def pages_of(design):
    pages = design.get("pages")
    if not pages:
        pages = [{"id": "p1", "elements": design.get("elements", [])}]
    for i, p in enumerate(pages, 1):
        p.setdefault("id", f"p{i}")
    return pages


def load_layout(name, cv, brand_dir=None):
    if not name:
        return {}
    places = [Path(brand_dir) / "thanh-phan" / "layouts" / f"{name}.json"] if brand_dir else []
    places.append(LAYOUT_DIR / f"{name}.json")
    f = next((p for p in places if p.exists()), None)
    if not f:
        die(f"Không có bố cục '{name}'. Xem `ia layouts`.")
    lay = read_json(f)
    rk = presets.ratio_key(cv["w"], cv["h"])
    variants = lay.get("variants", {})
    if rk in variants:
        return variants[rk]
    # gần nhất theo tỉ lệ
    def r(k):
        a, b = (float(x) for x in k.split(":"))
        return a / b
    target = cv["w"] / cv["h"]
    best = min(variants, key=lambda k: abs(r(k) - target)) if variants else None
    return variants.get(best, {})


# ------------------------------------------------------------------ tiện ích

def color(val, c, default=None):
    if val is None:
        return default
    if isinstance(val, str) and val in c:
        return c[val]
    return val


def px_box(box, cv):
    if box is None:
        return None
    if len(box) != 4:
        die(f"box phải có 4 số [x, y, w, h], đang là {box}")
    if all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in box):
        return [box[0] * cv["w"], box[1] * cv["h"], box[2] * cv["w"], box[3] * cv["h"]]
    return [float(v) for v in box]


def size_px(val, cv, default="md"):
    val = val or default
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str) and val.endswith("px"):
        return float(val[:-2])
    return SIZES.get(val, SIZES["md"]) * min(cv["w"], cv["h"]) * (1.25 if cv["w"] / cv["h"] > 1.6 else 1)


def rich(text, mark_style="color"):
    t = html.escape(str(text or ""))
    t = re.sub(r"\*\*(.+?)\*\*", rf'<mark class="m-{mark_style}">\1</mark>', t)
    return t.replace("\n", "<br>")


def asset_uri(src, job):
    if src.startswith(("http://", "https://", "data:", "file:")):
        return src
    p = Path(src).expanduser()
    if not p.is_absolute():
        p = Path(job) / src
    if not p.exists():
        die(f"Không thấy file ảnh: {src} (tìm ở {p})")
    return p.resolve().as_uri()


def icon_svg(name, col, size):
    f = RUNTIME / "icons" / f"{name}.svg"
    if not f.exists():
        return None
    svg = f.read_text(encoding="utf-8")
    svg = re.sub(r'width="\d+"', f'width="{size:.0f}"', svg, 1)
    svg = re.sub(r'height="\d+"', f'height="{size:.0f}"', svg, 1)
    return svg.replace("currentColor", col)


# ------------------------------------------------------------------ thành phần

def text_css(st, cv, c, fonts, default_size="md", default_font="body"):
    fam = fonts.get(st.get("font", default_font), fonts["body"])["family"]
    fs = size_px(st.get("size"), cv, default_size)
    css = [f"font-family:'{fam}',sans-serif", f"font-size:{fs:.0f}px",
           f"font-weight:{st.get('weight', 800 if default_font == 'heading' else 500)}",
           f"color:{color(st.get('color'), c, c['dark'])}", f"line-height:{st.get('line_height', 1.15 if default_font == 'heading' else 1.4)}",
           f"text-align:{st.get('align', 'left')}", f"letter-spacing:{st.get('tracking', '-0.01em' if default_font == 'heading' else '0')}"]
    if st.get("uppercase"):
        css.append("text-transform:uppercase")
    if st.get("stroke"):
        w, col = (st["stroke"].split() + ["#000"])[:2] if isinstance(st["stroke"], str) else (8, "#000")
        css.append(f"-webkit-text-stroke:{w}px {color(col, c)};paint-order:stroke fill")
    if st.get("shadow"):
        css.append("text-shadow:0 4px 18px rgba(0,0,0,.35)")
    return css, fs


def element_html(el, cv, c, fonts, brand, job, region):
    t = el.get("type", "text")
    st = dict(region.get("style", {}))
    st.update(el.get("style", {}))
    box = px_box(el.get("box"), cv) or px_box(region.get("box"), cv)
    if box is None:
        slot = el.get("slot") or el.get("role")
        die(f"Thành phần '{el.get('id')}' chưa có vị trí: thêm \"box\": [x,y,w,h] hoặc dùng bố cục có vùng '{slot}'.")
    x, y, w, h = box
    if t == "shape" and el.get("shape") == "circle" and abs(w - h) > 1:   # hình tròn luôn tròn, căn giữa vùng
        s = min(w, h)
        x, y, w, h = x + (w - s) / 2, y + (h - s) / 2, s, s
    valign = {"top": "flex-start", "center": "center", "bottom": "flex-end"}[st.get("valign", region.get("valign", "top"))]
    halign = {"left": "flex-start", "center": "center", "right": "flex-end"}.get(st.get("align", "left"), "flex-start")
    wrap = [f"left:{x:.1f}px", f"top:{y:.1f}px", f"width:{w:.1f}px", f"height:{h:.1f}px", f"z-index:{el.get('z', 2)}",
            "display:flex", "flex-direction:column", f"justify-content:{valign}"]
    if st.get("bg") and t not in ("button",):
        wrap.append(f"background:{color(st['bg'], c)}")
        wrap.append(f"border-radius:{st.get('radius', brand['radius'])}px")
        wrap.append(f"padding:{st.get('padding', round(min(w, h) * 0.08))}px")
    if st.get("mark_color"):
        wrap.append(f"--hl:{color(st['mark_color'], c)}")
    if st.get("opacity") is not None:
        wrap.append(f"opacity:{st['opacity']}")
    if st.get("rotate"):
        wrap.append(f"transform:rotate({st['rotate']}deg)")
    attrs = (f'data-id="{html.escape(str(el.get("id", "")))}" data-type="{t}" data-role="{html.escape(str(el.get("role", "")))}" '
             f'data-locked="{1 if el.get("content_locked") else 0}"')
    inner = ""
    if t == "text":
        heading = st.get("font", "heading" if el.get("role") in ("hook", "title", "headline", "stat", "number") else "body")
        css, fs = text_css(st, cv, c, fonts, region.get("size", "lg" if heading == "heading" else "md"), heading)
        min_fs = st.get("min_size", max(14, fs * 0.55))
        max_lines = st.get("max_lines", 0)
        if st.get("box_text"):  # mỗi dòng có nền riêng (kiểu thumbnail)
            css.append(f"--tb:{color(st['box_text'], c)}")
            inner = f'<div class="txt fit boxtext" data-min="{min_fs:.0f}" data-lines="{max_lines}" style="{";".join(css)}"><span>{rich(el.get("content"), st.get("mark", "color"))}</span></div>'
        else:
            inner = f'<div class="txt fit" data-min="{min_fs:.0f}" data-lines="{max_lines}" style="{";".join(css)}">{rich(el.get("content"), st.get("mark", "color"))}</div>'
    elif t == "list":
        css, fs = text_css(st, cv, c, fonts, region.get("size", "md"), st.get("font", "body"))
        icon = st.get("icon", el.get("icon", "check"))
        icol = color(st.get("icon_color"), c, c["primary"])
        rows = []
        for i, it in enumerate(el.get("items", [])):
            mark = icon_svg(icon, icol, fs * 1.1) if icon not in ("number", "dot") else None
            if not mark:
                sym = str(i + 1) if icon == "number" else ("•" if icon == "dot" else "✓")
                mark = f'<span class="badge" style="background:{icol};width:{fs * 1.5:.0f}px;height:{fs * 1.5:.0f}px;font-size:{fs * 0.8:.0f}px">{sym}</span>'
            rows.append(f'<div class="li" style="gap:{fs * 0.6:.0f}px;margin-bottom:{fs * st.get("gap", 0.7):.0f}px">'
                        f'<div class="lim">{mark}</div><div>{rich(it)}</div></div>')
        inner = f'<div class="txt fit list" data-min="{max(14, fs * 0.55):.0f}" style="{";".join(css)}">{"".join(rows)}</div>'
    elif t == "button":
        css, fs = text_css(st, cv, c, fonts, region.get("size", "md"), "heading")
        bg = color(st.get("bg"), c, c["primary"])
        css += [f"background:{bg}", f"color:{color(st.get('color'), c, '#FFFFFF')}", f"border-radius:{st.get('radius', 999)}px",
                f"padding:{fs * 0.55:.0f}px {fs * 1.2:.0f}px", "display:inline-block", "text-align:center"]
        inner = f'<div style="display:flex;justify-content:{halign}"><div class="txt btn" style="{";".join(css)}">{rich(el.get("content"))}</div></div>'
    elif t == "image":
        src = asset_uri(el.get("src") or die(f"Ảnh '{el.get('id')}' thiếu src."), job)
        fit = el.get("fit", "contain" if el.get("cutout") else "cover")
        pos = el.get("position", "center bottom" if el.get("cutout") else "center")
        filt = []
        if el.get("outline"):
            ow, ocol = (str(el["outline"]).split() + ["#FFFFFF"])[:2] if isinstance(el["outline"], str) else (8, "#FFFFFF")
            ocol = color(ocol, c)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                filt.append(f"drop-shadow({dx * int(ow)}px {dy * int(ow)}px 0 {ocol})")
        if el.get("shadow"):
            filt.append("drop-shadow(0 18px 30px rgba(0,0,0,.35))")
        rad = st.get("radius", 0 if el.get("cutout") else brand["radius"] if el.get("rounded") else 0)
        inner = (f'<img src="{src}" style="width:100%;height:100%;object-fit:{fit};object-position:{pos};'
                 f'border-radius:{rad}px;{"filter:" + " ".join(filt) if filt else ""}">')
    elif t == "logo":
        f = logo_file(brand, el.get("nen", "sang"))
        if f:
            inner = f'<img src="{f.as_uri()}" style="width:100%;height:100%;object-fit:contain;object-position:{el.get("position", "left center")}">'
        else:
            css, _ = text_css({"size": st.get("size", "sm"), "weight": 800, "color": st.get("color", "dark")}, cv, c, fonts, "sm", "heading")
            inner = f'<div class="txt" style="{";".join(css)}">{html.escape(brand["name"])}</div>'
    elif t == "icon":
        col = color(st.get("color"), c, c["primary"])
        svg = icon_svg(el.get("name", "star"), col, min(w, h))
        inner = svg or f'<div style="color:{col};font-size:{min(w, h) * 0.8:.0f}px;line-height:1;text-align:center">★</div>'
    elif t == "shape":
        fill = color(st.get("fill", el.get("fill")), c, c["primary"])
        shape = el.get("shape", "rect")
        rad = {"circle": "50%", "pill": "999px"}.get(shape, f"{st.get('radius', brand['radius'])}px")
        if shape == "line":
            inner = f'<div style="width:100%;height:{st.get("thickness", 6)}px;background:{fill};border-radius:9px"></div>'
        elif shape == "arrow":
            inner = (f'<svg viewBox="0 0 100 40" width="100%" height="100%" preserveAspectRatio="none"><path d="M2 20 H88 M70 4 L96 20 L70 36" '
                     f'fill="none" stroke="{fill}" stroke-width="{st.get("thickness", 7)}" stroke-linecap="round" stroke-linejoin="round"/></svg>')
        else:
            grad = st.get("gradient")
            bg = f"linear-gradient({grad[2] if len(grad) > 2 else 135}deg,{color(grad[0], c)},{color(grad[1], c)})" if grad else fill
            inner = f'<div style="width:100%;height:100%;background:{bg};border-radius:{rad}"></div>'
    elif t == "chart":
        spec = el.get("spec") or die(f"Biểu đồ '{el.get('id')}' thiếu spec.")
        inner = chartmod.render(spec, round(w), round(h), brand, fonts["body"]["family"])
        attrs += f' data-source="{html.escape(spec.get("source", ""))}"'
    elif t == "html":
        inner = el.get("html", "")
    else:
        die(f"Thành phần '{el.get('id')}': kiểu '{t}' chưa hỗ trợ (text, list, button, image, logo, icon, shape, chart, html).")
    return f'<div class="el" {attrs} style="{";".join(wrap)}">{inner}</div>'


def background(spec, c, job, w, h):
    spec = spec or {}
    if isinstance(spec, str):
        spec = {"color": spec}
    layers = []
    col = spec.get("color", "paper")
    if isinstance(col, str) and col.startswith("gradient:"):
        a, b, *ang = col[9:].split(",")
        bg = f"linear-gradient({ang[0] if ang else 135}deg,{color(a.strip(), c)},{color(b.strip(), c)})"
    else:
        bg = color(col, c, "#FFFFFF")
    if spec.get("transparent"):
        bg = "transparent"
    layers.append(f'<div class="bg" style="background:{bg}"></div>')
    if spec.get("image"):
        pos = spec.get("position", "center")
        layers.append(f'<div class="bg" style="background:url(\'{asset_uri(spec["image"], job)}\') {pos}/cover no-repeat"></div>')
    ov = spec.get("overlay")
    if ov == "dim":
        layers.append('<div class="bg" style="background:rgba(0,0,0,.45)"></div>')
    elif ov == "gradient-bottom":
        layers.append(f'<div class="bg" style="background:linear-gradient(180deg,rgba(0,0,0,0) 35%,{color(spec.get("overlay_color"), c, "rgba(0,0,0,.85)")} 100%)"></div>')
    elif ov == "gradient-left":
        layers.append(f'<div class="bg" style="background:linear-gradient(90deg,{color(spec.get("overlay_color"), c, "rgba(0,0,0,.85)")} 0%,rgba(0,0,0,0) 65%)"></div>')
    if spec.get("pattern") == "dots":
        layers.append(f'<div class="bg" style="background-image:radial-gradient({color(spec.get("pattern_color"), c, "rgba(0,0,0,.08)")} 2px,transparent 2px);background-size:{w // 30}px {w // 30}px"></div>')
    return "".join(layers)


def chrome(design, page, k, n, cv, c, fonts, brand):
    """Phần lặp lại của carousel: số trang, 'Vuốt →', handle — bật bằng design.chrome."""
    ch = design.get("chrome")
    if not ch or page.get("chrome") is False:
        return ""
    fs = size_px("xs", cv)
    dark = page.get("dark", False)
    col = "#FFFFFF" if dark else c["dark"]
    pad = cv["w"] * cv["safe"][0]
    bottom = cv["h"] * (1 - cv["safe"][1] - cv["safe"][3]) / 2 + fs * 0.2
    left = html.escape(ch.get("handle", brand.get("handle", "")) if ch.get("handle", True) else "")
    right = ""
    if ch.get("page_number", True):
        right = f"{k}/{n}"
    if ch.get("swipe", True) and k < n:
        right = (right + " · " if right else "") + ch.get("swipe_text", "Vuốt →")
    return (f'<div class="chrome" style="left:{pad:.0f}px;right:{pad:.0f}px;bottom:{bottom:.0f}px;font-family:\'{fonts["body"]["family"]}\';'
            f'font-size:{fs:.0f}px;color:{col}"><span>{left}</span><span>{html.escape(right)}</span></div>')


CSS = """
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:transparent}
.page{position:relative;overflow:hidden;margin:0 0 40px 0}
.bg{position:absolute;inset:0}
.el{position:absolute}
.txt{overflow-wrap:break-word;hyphens:none}
mark{background:none;color:var(--hl)}
mark.m-box{background:var(--hl);color:#fff;padding:0 .18em;border-radius:.12em;-webkit-box-decoration-break:clone;box-decoration-break:clone}
mark.m-underline{color:inherit;background:linear-gradient(transparent 62%,var(--hl) 62%,var(--hl) 92%,transparent 92%)}
.boxtext span{background:var(--tb);padding:.06em .28em;line-height:1.5;-webkit-box-decoration-break:clone;box-decoration-break:clone;border-radius:.1em}
.li{display:flex;align-items:flex-start}
.lim{flex:none;display:flex;align-items:center;justify-content:center;padding-top:.1em}
.badge{display:inline-flex;align-items:center;justify-content:center;border-radius:50%;color:#fff;font-weight:800}
.chrome{position:absolute;display:flex;justify-content:space-between;font-weight:600;opacity:.75;z-index:50}
"""


def compose(design, brand, job):
    cv = canvas_of(design)
    c = brand["colors"]
    fonts = brand["fonts"]
    fcss, missing = font_css(brand)
    pages = pages_of(design)
    n = len(pages)
    secs = []
    for k, page in enumerate(pages, 1):
        lay = load_layout(page.get("layout", design.get("layout")), cv, brand["dir"])
        regions = lay.get("regions", {})
        bg = page.get("bg", design.get("bg", lay.get("bg")))
        els = []
        for el in page.get("elements", []):
            region = regions.get(el.get("slot") or el.get("role"), {})
            els.append(element_html(el, cv, c, fonts, brand, job, region))
        transparent = isinstance(bg, dict) and bg.get("transparent")
        secs.append(f'<section class="page{" transparent" if transparent else ""}" id="{page["id"]}" '
                    f'style="width:{cv["w"]}px;height:{cv["h"]}px">{background(bg, c, job, cv["w"], cv["h"])}'
                    f'{"".join(els)}{chrome(design, page, k, n, cv, c, fonts, brand)}</section>')
    root = f":root{{--hl:{c['highlight']};--primary:{c['primary']};--dark:{c['dark']}}}"
    doc = (f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><style>{fcss}\n{CSS}\n{root}</style></head>'
           f'<body>{"".join(secs)}</body></html>')
    return doc, cv, pages, missing

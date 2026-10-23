"""Biểu đồ → SVG theo màu brand (không cần thư viện ngoài). Dùng trong design.json (element type "chart") hoặc:

  ia chart <spec.json> --out bieu-do.svg [--w 1200 --h 700]

spec:
{
  "kind": "bar" | "hbar" | "line" | "donut" | "funnel" | "table" | "compare",
  "title": "…",                       (tuỳ chọn — thường đặt tiêu đề ở element text riêng)
  "unit": "%" | "đ" | "",             đơn vị hiển thị sau số
  "labels": ["T1", "T2", …],
  "series": [{"name": "Chi phí", "values": [12, 18, …], "color": "primary"}],
  "highlight": 2,                     cột/điểm cần nhấn (chỉ số, từ 0)
  "source": "Meta Ads Manager, 01–31/10/2026"   BẮT BUỘC — biểu đồ không nguồn sẽ bị QA chặn
  "rows": [["Tiêu chí", "Trước", "Sau"], …]     (kind table / compare)
}
Không tự đặt ra số liệu: mọi con số phải đến từ người dùng, Brief đã duyệt hoặc file dữ liệu.
"""
import html
import math

from common import die, read_json


def _fmt(v, unit=""):
    if isinstance(v, (int, float)):
        s = f"{v:,.0f}" if abs(v) >= 100 or float(v).is_integer() else f"{v:,.1f}"
        s = s.replace(",", ".") if abs(v) >= 1000 else s
    else:
        s = str(v)
    return f"{s}{unit}"


def _color(name, colors):
    return colors.get(name, name) if name else colors["primary"]


def render(spec, w, h, brand, font="Be Vietnam Pro"):
    c = brand["colors"]
    kind = spec.get("kind", "bar")
    unit = spec.get("unit", "")
    ink, muted, grid = c["dark"], _mix(c["dark"], "#FFFFFF", 0.45), _mix(c["dark"], "#FFFFFF", 0.88)
    fs = max(14, round(min(w, h) * 0.035))
    parts = []
    t = lambda x, y, s, size=fs, wt=500, fill=ink, anchor="middle": parts.append(
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{wt}" fill="{fill}" text-anchor="{anchor}">{html.escape(str(s))}</text>')
    top = 0
    if spec.get("title"):
        t(w / 2, fs * 1.4, spec["title"], fs * 1.3, 800)
        top = fs * 2.2
    bottom = fs * 2.0 if spec.get("source") else 0
    if spec.get("source"):
        t(8, h - fs * 0.6, "Nguồn: " + spec["source"], fs * 0.72, 400, muted, "start")
    labels = spec.get("labels", [])
    series = spec.get("series", [])
    hi = spec.get("highlight")
    if kind in ("bar", "hbar", "line"):
        if not series or not labels:
            die("Biểu đồ cần 'labels' và 'series'.")
        vals = [v for s in series for v in s["values"]]
        vmax = max(vals) * 1.15 if max(vals) > 0 else 1
        L, R, T, B = fs * 1.0, w - fs * 1.0, top + fs * 1.6, h - bottom - fs * 2.2
        if kind == "hbar":
            L = fs * 0.6 + max(len(str(lb)) for lb in labels) * fs * 0.55
        n, k = len(labels), len(series)
        if kind in ("bar", "line"):
            for g in range(5):
                y = B - (B - T) * g / 4
                parts.append(f'<line x1="{L}" y1="{y:.1f}" x2="{R}" y2="{y:.1f}" stroke="{grid}" stroke-width="2"/>')
        if kind == "bar":
            slot = (R - L) / n
            bw = slot * 0.62 / k
            for i, lb in enumerate(labels):
                for j, s in enumerate(series):
                    v = s["values"][i]
                    bh = (B - T) * v / vmax
                    x = L + slot * i + slot * 0.19 + bw * j
                    col = _color(s.get("color"), c) if hi is None or hi == i else _mix(_color(s.get("color"), c), "#FFFFFF", 0.55)
                    parts.append(f'<rect x="{x:.1f}" y="{B - bh:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="{min(10, bw / 4):.1f}" fill="{col}"/>')
                    t(x + bw / 2, B - bh - fs * 0.45, _fmt(v, unit), fs * 0.9, 700)
                t(L + slot * i + slot / 2, B + fs * 1.3, lb, fs * 0.85, 500, muted)
        elif kind == "hbar":
            slot = (B - T) / n
            bh = slot * 0.6 / k
            for i, lb in enumerate(labels):
                for j, s in enumerate(series):
                    v = s["values"][i]
                    bw = (R - L - fs * 3) * v / vmax
                    y = T + slot * i + slot * 0.2 + bh * j
                    col = _color(s.get("color"), c) if hi is None or hi == i else _mix(_color(s.get("color"), c), "#FFFFFF", 0.55)
                    parts.append(f'<rect x="{L:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{bh:.1f}" rx="{min(10, bh / 4):.1f}" fill="{col}"/>')
                    t(L + bw + fs * 0.4, y + bh / 2 + fs * 0.35, _fmt(v, unit), fs * 0.9, 700, ink, "start")
                t(L - fs * 0.5, T + slot * i + slot / 2 + fs * 0.35, lb, fs * 0.85, 500, muted, "end")
        else:
            step = (R - L) / max(1, n - 1)
            for j, s in enumerate(series):
                col = _color(s.get("color"), c)
                pts = [(L + step * i, B - (B - T) * v / vmax) for i, v in enumerate(s["values"])]
                parts.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="none" stroke="{col}" stroke-width="{max(4, fs / 5):.0f}" stroke-linejoin="round" stroke-linecap="round"/>')
                for i, (x, y) in enumerate(pts):
                    r = fs * 0.45 if hi == i else fs * 0.28
                    parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}"/>')
                    if hi is None or hi == i or i == len(pts) - 1:
                        t(x, y - fs * 0.8, _fmt(s["values"][i], unit), fs * 0.9, 700)
            for i, lb in enumerate(labels):
                t(L + step * i, B + fs * 1.3, lb, fs * 0.85, 500, muted)
        if k > 1:
            x = L
            for s in series:
                col = _color(s.get("color"), c)
                parts.append(f'<rect x="{x:.1f}" y="{top + fs * 0.2:.1f}" width="{fs * 0.8:.1f}" height="{fs * 0.8:.1f}" rx="4" fill="{col}"/>')
                t(x + fs * 1.1, top + fs * 0.95, s["name"], fs * 0.85, 600, ink, "start")
                x += fs * 2 + len(s["name"]) * fs * 0.55
    elif kind == "donut":
        vals = series[0]["values"] if series else spec.get("values", [])
        tot = sum(vals) or 1
        cx, cy = w * 0.32, top + (h - top - bottom) / 2
        R = min(w * 0.28, (h - top - bottom) * 0.44)
        palette = [c["primary"], c["highlight"], c["secondary"], _mix(c["primary"], "#FFFFFF", 0.5), _mix(c["dark"], "#FFFFFF", 0.6)]
        a0 = -math.pi / 2
        for i, v in enumerate(vals):
            a1 = a0 + 2 * math.pi * v / tot
            large = 1 if a1 - a0 > math.pi else 0
            x0, y0, x1, y1 = cx + R * math.cos(a0), cy + R * math.sin(a0), cx + R * math.cos(a1 - 1e-4), cy + R * math.sin(a1 - 1e-4)
            parts.append(f'<path d="M{x0:.1f},{y0:.1f} A{R:.1f},{R:.1f} 0 {large} 1 {x1:.1f},{y1:.1f}" fill="none" '
                         f'stroke="{palette[i % len(palette)]}" stroke-width="{R * 0.36:.1f}"/>')
            a0 = a1
        if hi is not None:
            t(cx, cy + fs * 0.6, _fmt(round(vals[hi] / tot * 100), "%"), fs * 2.2, 800)
        for i, lb in enumerate(labels):
            y = cy - (len(labels) - 1) * fs * 0.9 + i * fs * 1.8
            parts.append(f'<rect x="{w * 0.62:.1f}" y="{y - fs * 0.7:.1f}" width="{fs * 0.9:.1f}" height="{fs * 0.9:.1f}" rx="4" fill="{palette[i % len(palette)]}"/>')
            t(w * 0.62 + fs * 1.4, y + fs * 0.1, f"{lb} — {_fmt(vals[i], unit)}", fs, 600, ink, "start")
    elif kind == "funnel":
        vals = series[0]["values"]
        n = len(vals)
        T, B = top + fs, h - bottom - fs * 0.5
        sh = (B - T) / n
        for i, v in enumerate(vals):
            ww = w * 0.86 * (1 - i * 0.55 / max(1, n - 1))
            x = (w - ww) / 2
            col = _mix(c["primary"], "#FFFFFF", i * 0.5 / max(1, n - 1)) if hi is None or hi != i else c["highlight"]
            parts.append(f'<rect x="{x:.1f}" y="{T + sh * i + 4:.1f}" width="{ww:.1f}" height="{sh - 8:.1f}" rx="{sh * 0.18:.1f}" fill="{col}"/>')
            fill = "#FFFFFF" if i < n * 0.6 or hi == i else ink
            t(w / 2, T + sh * i + sh / 2 + fs * 0.35, f"{labels[i]}: {_fmt(v, unit)}", fs * 1.05, 700, fill)
            if i > 0 and vals[i - 1]:
                t(x + ww + fs * 0.3, T + sh * i + fs * 0.5, f"↓ {v / vals[i - 1] * 100:.1f}%", fs * 0.8, 600, muted, "start")
    elif kind in ("table", "compare"):
        rows = spec.get("rows") or die("Bảng cần 'rows'.")
        ncol, nrow = len(rows[0]), len(rows)
        T, B = top + fs * 0.5, h - bottom - fs * 0.5
        rh = (B - T) / nrow
        cw = w / ncol
        for r, row in enumerate(rows):
            y = T + rh * r
            if r == 0:
                parts.append(f'<rect x="0" y="{y:.1f}" width="{w}" height="{rh:.1f}" rx="12" fill="{c["primary"]}"/>')
            elif r % 2 == 0:
                parts.append(f'<rect x="0" y="{y:.1f}" width="{w}" height="{rh:.1f}" fill="{grid}"/>')
            for k2, cell in enumerate(row):
                fill = "#FFFFFF" if r == 0 else (c["primary"] if kind == "compare" and k2 == ncol - 1 else ink)
                anchor = "start" if k2 == 0 else "middle"
                x = fs * 0.8 if k2 == 0 else cw * k2 + cw / 2
                t(x, y + rh / 2 + fs * 0.35, cell, fs, 800 if r == 0 or (kind == "compare" and k2 == ncol - 1) else 500, fill, anchor)
    else:
        die(f"Loại biểu đồ '{kind}' chưa hỗ trợ (bar, hbar, line, donut, funnel, table, compare).")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" '
            f'font-family="\'{font}\', sans-serif">' + "".join(parts) + "</svg>")


def _mix(a, b, t):
    a, b = a.lstrip("#"), b.lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02X}" for x, y in zip(ca, cb))


def main(args):
    import brand as brandmod
    from pathlib import Path
    if not args:
        die(__doc__)
    spec = read_json(args[0])
    out = Path(args[args.index("--out") + 1]) if "--out" in args else Path(args[0]).with_suffix(".svg")
    w = int(args[args.index("--w") + 1]) if "--w" in args else 1200
    h = int(args[args.index("--h") + 1]) if "--h" in args else 700
    b = brandmod.load()
    if not spec.get("source"):
        print("⚠️ Biểu đồ chưa có 'source' (nguồn số liệu) — QA sẽ chặn khi bàn giao.")
    out.write_text(render(spec, w, h, b, b["fonts"]["body"]["family"]), encoding="utf-8")
    print(f"Đã vẽ {out}")
    return 0

"""Mockup: đặt thiết kế lên điện thoại / laptop / bìa sách / tờ in — vẽ bằng CSS, không dùng ảnh thiết bị của bên khác.

  ia mockup <ảnh> --kieu dien-thoai|laptop|sach|the [--nen <màu|tên màu brand>] [--khung 1080x1350] [--out <file.png>]

Ảnh nên đúng tỉ lệ màn hình: điện thoại 9:19.5 (ảnh dọc, phần thừa bị cắt từ dưới), laptop 16:10, sách 2:3, tờ in theo tỉ lệ ảnh.
Dùng: bán khoá học / ebook (sách), giới thiệu app / landing (điện thoại, laptop), ấn phẩm in (the).
"""
import base64
import mimetypes
from pathlib import Path

from common import die, info, warn

KIEU = ("dien-thoai", "laptop", "sach", "the")

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%(W)dpx;height:%(H)dpx;background:%(bg)s;overflow:hidden}
.stage{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
.shadow{filter:drop-shadow(0 %(s1)dpx %(s2)dpx rgba(20,20,40,.28))}
/* điện thoại */
.phone{width:%(pw)dpx;height:%(ph)dpx;border-radius:%(pr)dpx;background:#111318;padding:%(pb)dpx;position:relative}
.phone .scr{width:100%%;height:100%%;border-radius:%(sr)dpx;overflow:hidden;background:#fff}
.phone .scr img{width:100%%;height:100%%;object-fit:cover;object-position:top center;display:block}
.phone .notch{position:absolute;top:%(nt)dpx;left:50%%;transform:translateX(-50%%);width:%(nw)dpx;height:%(nh)dpx;border-radius:99px;background:#111318}
/* laptop */
.laptop{display:flex;flex-direction:column;align-items:center}
.laptop .lid{width:%(lw)dpx;height:%(lh)dpx;background:#16181d;border-radius:%(lr)dpx %(lr)dpx 0 0;padding:%(lb)dpx}
.laptop .lid img{width:100%%;height:100%%;object-fit:cover;object-position:top center;display:block;border-radius:4px}
.laptop .base{width:%(bw)dpx;height:%(bh)dpx;background:linear-gradient(#d9dbe1,#b9bcc5);border-radius:0 0 %(br)dpx %(br)dpx;position:relative}
.laptop .base:after{content:"";position:absolute;top:0;left:50%%;transform:translateX(-50%%);width:18%%;height:40%%;background:#a6a9b2;border-radius:0 0 10px 10px}
/* sách */
.bookwrap{perspective:%(pp)dpx}
.book{width:%(kw)dpx;height:%(kh)dpx;position:relative;transform:rotateY(-24deg) rotateX(4deg);transform-style:preserve-3d}
.book .cover{position:absolute;inset:0;overflow:hidden;border-radius:2px 8px 8px 2px}
.book .cover img{width:100%%;height:100%%;object-fit:cover;display:block}
.book .cover:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.28) 0,rgba(255,255,255,.18) 2.5%%,rgba(0,0,0,0) 6%%,rgba(0,0,0,0) 100%%)}
.book .pages{position:absolute;top:1.5%%;right:-%(kd)dpx;width:%(kd)dpx;height:97%%;background:repeating-linear-gradient(90deg,#fff 0 2px,#e9e9ee 2px 3px);transform:rotateY(90deg);transform-origin:left}
/* tờ in */
.card{transform:rotate(-4deg)}
.card img{display:block;max-width:%(cw)dpx;max-height:%(ch)dpx;border-radius:3px}
"""

BODY = {
    "dien-thoai": '<div class="phone shadow"><div class="notch"></div><div class="scr"><img src="{src}"></div></div>',
    "laptop": '<div class="laptop shadow"><div class="lid"><img src="{src}"></div><div class="base"></div></div>',
    "sach": '<div class="bookwrap shadow"><div class="book"><div class="cover"><img src="{src}"></div><div class="pages"></div></div></div>',
    "the": '<div class="card shadow"><img src="{src}"></div>',
}


def _bg(val):
    if not val:
        try:
            import brand as brandmod
            return brandmod.load()["colors"].get("light", "#F3F2F7")
        except SystemExit:
            return "#F3F2F7"
    if val.startswith("#") or val.startswith("rgb") or val.startswith("linear"):
        return val
    try:
        import brand as brandmod
        return brandmod.load()["colors"].get(val, val)
    except SystemExit:
        return val


def render(src, kieu, out, W=1080, H=1350, bg=None):
    from playwright.sync_api import sync_playwright
    src = Path(src)
    mime = mimetypes.guess_type(src.name)[0] or "image/png"
    data = f"data:{mime};base64," + base64.b64encode(src.read_bytes()).decode()
    m = min(W, H)
    ph = H * 0.84 if H >= W else H * 0.86
    pw = ph / 2.05
    lw = min(W * 0.86, H * 0.62 * 1.6)
    lh = lw / 1.6
    kh = min(H * 0.72, W * 0.6 * 1.5)
    kw = kh / 1.5
    vals = dict(W=W, H=H, bg=_bg(bg), s1=m * 0.03, s2=m * 0.05,
                pw=pw, ph=ph, pr=pw * 0.14, pb=pw * 0.035, sr=pw * 0.11, nt=pw * 0.05, nw=pw * 0.3, nh=pw * 0.07,
                lw=lw, lh=lh, lr=lw * 0.03, lb=lw * 0.025, bw=lw * 1.16, bh=lw * 0.035, br=lw * 0.03,
                pp=kw * 4, kw=kw, kh=kh, kd=kw * 0.09, cw=W * 0.74, ch=H * 0.8)
    html = f"<!doctype html><html><head><meta charset='utf-8'><style>{CSS % vals}</style></head>" \
           f"<body><div class='stage'>{BODY[kieu].format(src=data)}</div></body></html>"
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as pw_:
        br = pw_.chromium.launch()
        pg = br.new_page(viewport={"width": W, "height": H})
        pg.set_content(html)
        pg.wait_for_load_state("networkidle")
        pg.screenshot(path=str(out))
        br.close()
    return out


def main(args):
    if not args or args[0].startswith("--"):
        die(__doc__)

    def opt(name, default=None):
        return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else default

    src = Path(args[0]).expanduser()
    if not src.exists():
        die(f"Không thấy ảnh {src}")
    kieu = opt("--kieu") or die("Thiếu --kieu (" + ", ".join(KIEU) + ")")
    if kieu not in KIEU:
        die("--kieu chỉ nhận: " + ", ".join(KIEU))
    W, H = (int(x) for x in (opt("--khung", "1080x1350")).lower().split("x"))
    out = Path(opt("--out") or src.with_name(f"{src.stem}-mockup-{kieu}.png"))
    from PIL import Image
    im = Image.open(src)
    want = {"dien-thoai": 9 / 19.5, "laptop": 16 / 10, "sach": 2 / 3}.get(kieu)
    if want and abs(im.width / im.height - want) / want > 0.25:
        warn(f"Ảnh {im.width}×{im.height} khác tỉ lệ màn hình {kieu} — phần thừa sẽ bị cắt (giữ phần trên).")
    render(src, kieu, out, W, H, opt("--nen"))
    info(f"Mockup: {out}")
    return 0

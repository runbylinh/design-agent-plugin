"""Tách nền (chạy trên máy, không gửi ảnh ra ngoài) + phóng to dự phòng + đo chất lượng ảnh thô.

  ia cutout <ảnh> [--model isnet-general-use|birefnet-portrait|birefnet-general|u2net_human_seg] [--out x.png] [--job DS]
  ia upscale <ảnh> [--x 2] [--out x.png]      phóng to thường (Lanczos) — KHÔNG phải AI; ưu tiên Higgsfield upscale_image khi được phép
  ia inspect <ảnh…>                           kích thước, độ nét, độ sáng → ảnh có đủ dùng cho khổ nào

Chỉ tách nền ảnh có vai trò "chủ thể" (người, sản phẩm). Ảnh bối cảnh / nền tràn / ảnh chụp màn hình: KHÔNG tách.
Model mặc định isnet-general-use (~170MB, tự tải lần đầu). Tóc xoà, viền khó → thử birefnet-portrait (người) / birefnet-general.
Sau khi tách luôn mở <tên>-kiem-vien.png để xem viền; viền xấu → thêm "outline" trong design.json, đổi model, hoặc Higgsfield remove_background.
"""
import os
from pathlib import Path

from common import RUNTIME, die, info, manifest, save_manifest, log, warn

os.environ.setdefault("U2NET_HOME", str(RUNTIME / "models"))


def opt(args, name, default=None):
    return args[args.index(name) + 1] if name in args else default


def cutout(args):
    from PIL import Image
    if not args or args[0].startswith("--"):
        die(__doc__)
    src = Path(args[0]).expanduser()
    if not src.exists():
        die(f"Không thấy ảnh {src}")
    model = opt(args, "--model", "isnet-general-use")
    job = opt(args, "--job")
    if job:
        m = manifest(job)
        default_out = Path(m["_dir"]) / "assets" / f"{src.stem}-tach-nen.png"
    else:
        default_out = src.with_name(f"{src.stem}-tach-nen.png")
    out = Path(opt(args, "--out", default_out))
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        from rembg import new_session, remove
    except ImportError:
        die("Chưa cài rembg. Chạy `ia setup`.")
    info(f"Tách nền bằng {model} (lần đầu sẽ tải model)…")
    im = Image.open(src)
    im.load()
    res = remove(im.convert("RGBA"), session=new_session(model), post_process_mask=True)
    alpha = res.split()[3]
    bbox = alpha.point(lambda a: 255 if a > 24 else 0).getbbox()
    if not bbox:
        die("Không tìm thấy chủ thể trong ảnh — ảnh này không hợp để tách nền.")
    W, H = res.size
    notes = []
    area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1]) / (W * H)
    if area < 0.05:
        notes.append("chủ thể rất nhỏ trong ảnh → phóng to sẽ vỡ, cân nhắc ảnh khác")
    edges = [n for n, hit in (("trái", bbox[0] <= 2), ("trên", bbox[1] <= 2), ("phải", bbox[2] >= W - 2)) if hit]
    if edges:
        notes.append(f"chủ thể chạm mép {', '.join(edges)} của ảnh gốc (bị cắt sẵn) → đặt sát mép khung tương ứng")
    hist = alpha.histogram()
    semi = sum(hist[25:230]) / max(1, sum(hist[25:]))
    if semi > 0.12:
        notes.append(f"viền mờ nhiều ({semi * 100:.0f}% điểm bán trong suốt) — kiểm tóc/viền; có thể thử model birefnet-portrait")
    pad = round(max(W, H) * 0.01)
    crop = res.crop((max(0, bbox[0] - pad), max(0, bbox[1] - pad), min(W, bbox[2] + pad), min(H, bbox[3] + pad)))
    crop.save(out)
    # ảnh kiểm viền: trên nền tối + nền ca-rô
    cw, ch = crop.size
    sheet = Image.new("RGB", (cw * 2 + 30, ch + 20), (40, 40, 40))
    checker = Image.new("RGB", (cw, ch), (255, 255, 255))
    tile = max(8, cw // 40)
    for yy in range(0, ch, tile):
        for xx in range(0, cw, tile):
            if (xx // tile + yy // tile) % 2:
                checker.paste((204, 204, 204), (xx, yy, xx + tile, yy + tile))
    dark = Image.new("RGB", (cw, ch), (24, 24, 32))
    checker.paste(crop, mask=crop.split()[3])
    dark.paste(crop, mask=crop.split()[3])
    sheet.paste(checker, (10, 10))
    sheet.paste(dark, (cw + 20, 10))
    chk = out.with_name(out.stem + "-kiem-vien.png")
    sheet.thumbnail((1600, 1600))
    sheet.save(chk)
    info(f"Đã tách nền → {out}  ({cw}×{ch})")
    info(f"Xem viền: {chk}")
    for n in notes:
        warn(n)
    if job:
        m = manifest(job)
        m.setdefault("tai_nguyen", []).append({"file": str(out.relative_to(m["_dir"])) if str(out).startswith(m["_dir"]) else str(out),
                                               "nguon": f"tách nền {src.name} ({model})", "goc": str(src)})
        log(m, f"tách nền {src.name} ({model})")
        save_manifest(m)
    return 0


def upscale(args):
    from PIL import Image, ImageFilter
    src = Path(args[0]).expanduser() if args else die(__doc__)
    k = float(opt(args, "--x", 2))
    out = Path(opt(args, "--out", src.with_name(f"{src.stem}-x{k:g}{src.suffix}")))
    im = Image.open(src)
    big = im.resize((round(im.width * k), round(im.height * k)), Image.Resampling.LANCZOS)
    big = big.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))
    big.save(out)
    warn("Phóng to thường (không phải AI) — chi tiết không tăng thêm. Ảnh quan trọng → dùng Higgsfield upscale_image nếu được phép gửi ảnh ra ngoài.")
    info(f"Đã phóng → {out} ({big.width}×{big.height})")
    return 0


def inspect(args):
    from PIL import Image, ImageFilter, ImageStat
    if not args:
        die(__doc__)
    for a in args:
        p = Path(a).expanduser()
        if not p.exists():
            warn(f"Không thấy {p}")
            continue
        im = Image.open(p)
        g = im.convert("L")
        small = g.copy()
        small.thumbnail((800, 800))
        sharp = ImageStat.Stat(small.filter(ImageFilter.FIND_EDGES)).var[0]
        bright = ImageStat.Stat(small).mean[0]
        alpha = im.mode == "RGBA" and im.getextrema()[3][0] < 255
        fits = []
        for name, (w, h) in {"thumbnail 1280×720": (1280, 720), "4:5 1080×1350": (1080, 1350), "9:16 1080×1920": (1080, 1920)}.items():
            if im.width >= w * 0.5 and im.height >= h * 0.5:
                fits.append(name)
        verdict = []
        if sharp < 60:
            verdict.append("mờ/thiếu nét")
        if bright < 55:
            verdict.append("tối")
        if bright > 215:
            verdict.append("cháy sáng")
        info(f"{p.name}: {im.width}×{im.height} {'(có nền trong suốt) ' if alpha else ''}· nét {sharp:.0f} · sáng {bright:.0f}"
             f" · {'⚠️ ' + ', '.join(verdict) if verdict else 'ổn'} · đủ cỡ làm chủ thể nửa khung: {', '.join(fits) or 'KHÔNG — quá nhỏ'}")
    return 0


def main(cmd, args):
    return {"cutout": cutout, "upscale": upscale, "inspect": inspect}[cmd](args)

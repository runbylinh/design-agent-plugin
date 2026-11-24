"""Xuất thành phẩm từ bản ĐÃ DUYỆT + kiểm tra sau xuất (QA lần 2, phần máy làm).

  ia export <DS> [--dinh-dang png,jpg,webp,pdf,pptx] [--max-kb 500] [--cmyk]
  ia check <DS>                      kiểm lại bộ file đã xuất (mở từng file, kích thước, trong suốt, dung lượng, đủ trang)

Thành phẩm ở jobs/<DS>/approved/:
  <DS>-<trang>.png|jpg|webp    (trang = id trang: p1…, hoặc Scene ID SC-03 với đồ hoạ video)
  <DS>.pdf                     (carousel / poster in: gộp mọi trang)
  design.json · source.html · assets/ · manifest.json    (file nguồn để mở lại sửa sau này)
  xem-dien-thoai/              bản thu nhỏ để xem độ dễ đọc
Mặc định định dạng lấy từ design.json → export.formats, không có thì: PNG (+PDF nếu nhiều trang).
"""
import shutil
from pathlib import Path

import brand as brandmod
from common import die, file_hash, info, log, manifest, read_json, save_manifest, version_dir, warn, write_json
from render import MOBILE_WIDTH, render_design


def opt(args, name, default=None):
    return args[args.index(name) + 1] if name in args else default


def _save(img, path, fmt, max_kb, transparent):
    from PIL import Image
    if fmt == "png":
        img.save(path, optimize=True)
        if max_kb and path.stat().st_size > max_kb * 1024 and not transparent:
            q = img.convert("RGB").quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG)
            q.save(path, optimize=True)
        return
    rgb = img
    if fmt in ("jpg", "jpeg"):
        if img.mode == "RGBA":
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=img.split()[3])
            rgb = bg
        else:
            rgb = img.convert("RGB")
    for q in (92, 88, 84, 80, 76, 72, 68, 64, 60):
        if fmt in ("jpg", "jpeg"):
            rgb.save(path, "JPEG", quality=q, optimize=True, progressive=True, subsampling=0 if q >= 88 else 2)
        else:
            rgb.save(path, "WEBP", quality=q, method=6)
        if not max_kb or path.stat().st_size <= max_kb * 1024:
            break


def export(args):
    from PIL import Image
    m = manifest(args[0] if args else die(__doc__))
    bd = m.get("ban_duyet") or die(f"{m['design_id']} chưa có bản được duyệt. Duyệt trước: `ia approve {m['design_id']} --v N --xac-nhan \"…\"`.", 2)
    vd = version_dir(m, bd["v"]) / (f"huong-{bd['huong']}" if bd.get("huong") else "")
    design = read_json(vd / "design.json")
    b = brandmod.load(design.get("brand") or m.get("brand"))
    # dựng lại từ design.json đã duyệt để chắc chắn file xuất đúng bản duyệt
    qa, files = render_design(design, b, m["_dir"], vd, m.get("noi_dung_khoa") or None, keep_bare=True)
    if qa["loi"] and "--chap-nhan-loi" not in args:
        die("Bản duyệt dựng lại có lỗi chặn:\n  " + "\n  ".join(qa["loi"]), 2)
    ex = design.get("export", {})
    fmts = [f.strip().lower() for f in (opt(args, "--dinh-dang") or ",".join(ex.get("formats", []))).split(",") if f.strip()]
    max_kb = int(opt(args, "--max-kb", ex.get("max_kb", 0)) or 0)
    transparent = any(isinstance(p.get("bg", design.get("bg")), dict) and p.get("bg", design.get("bg")).get("transparent")
                      for p in design.get("pages", [{}]))
    import presets as _pre
    prn = (_pre.PRESETS.get((design.get("canvas") or {}).get("preset") or "", {}) or {}).get("print")
    if not fmts:
        fmts = ["png"] + (["pdf"] if (len(files) > 1 or prn) and not transparent else [])
    if prn and "pdf" not in fmts:
        fmts.append("pdf")
    out = Path(m["_dir"]) / "approved"
    if out.exists():
        shutil.rmtree(out)
    (out / "xem-dien-thoai").mkdir(parents=True)
    did = m["design_id"]
    made = []
    imgs = []
    for f in files:
        im = Image.open(f)
        im.load()
        imgs.append((f.stem, im))
        for fmt in fmts:
            if fmt in ("pdf", "pptx"):
                continue
            if transparent and fmt in ("jpg", "jpeg"):
                warn("Thiết kế nền trong suốt → bỏ JPG (JPG không giữ được trong suốt), xuất PNG.")
                continue
            p = out / f"{did}-{f.stem}.{ 'jpg' if fmt == 'jpeg' else fmt}"
            _save(im, p, fmt, max_kb, transparent)
            made.append(p.name)
        sc = MOBILE_WIDTH.get("16:9" if im.width / im.height > 1.5 else "4:5", 390) / im.width
        im.convert("RGB").resize((round(im.width * sc), round(im.height * sc))).save(out / "xem-dien-thoai" / f"{f.stem}.png")
    if "pdf" in fmts:
        rgb = [im.convert("RGB") for _, im in imgs]
        dpi = prn["dpi"] if prn else 150
        rgb[0].save(out / f"{did}.pdf", save_all=True, append_images=rgb[1:], resolution=dpi)
        made.append(f"{did}.pdf")
        if prn and "--cmyk" in args:
            cm = [im.convert("CMYK") for im in rgb]
            cm[0].save(out / f"{did}-cmyk.pdf", save_all=True, append_images=cm[1:], resolution=dpi)
            made.append(f"{did}-cmyk.pdf")
        if prn:
            info(f"File in: {prn['mm'][0]}×{prn['mm'][1]}mm + tràn lề {prn['bleed_mm']}mm mỗi cạnh, {dpi}dpi — báo xưởng in: đã có tràn lề, xén theo kích thước thật.")
    if "pptx" in fmts:
        import pptx_export
        pptx_export.build(vd, out / f"{did}.pptx", design)
        made.append(f"{did}.pptx")
    # file nguồn
    shutil.copy2(vd / "design.json", out / "design.json")
    shutil.copy2(vd / "index.html", out / "source.html")
    if (Path(m["_dir"]) / "assets").exists():
        shutil.copytree(Path(m["_dir"]) / "assets", out / "assets")
    m["xuat"] = {"luc": __import__("common").now(), "tu": f"v{bd['v']}", "files": made, "dinh_dang": fmts, "max_kb": max_kb,
                 "trong_suot": transparent, "kich_thuoc": qa["kich_thuoc"], "trang": qa["trang"]}
    m["trang_thai"] = "Đã duyệt"
    log(m, f"xuất {len(made)} file từ v{bd['v']}")
    save_manifest(m)
    shutil.copy2(Path(m["_dir"]) / "manifest.json", out / "manifest.json")
    info(f"Đã xuất {len(made)} file → {out}")
    code = check([did])
    import tracker
    m = manifest(did)
    q = m["xuat"].get("qa_sau_xuat", {})
    tracker.recap(did, bd["v"], "Xuất", f"Xuất {', '.join(made)}", qa_may=f"QA sau xuất: {q.get('loi', 0)} lỗi, {q.get('canh_bao', 0)} cảnh báo")
    tracker.hint_push()
    return code


def check(args):
    from PIL import Image
    m = manifest(args[0] if args else die("ia check <DS>"))
    x = m.get("xuat") or die("Chưa xuất file. Chạy `ia export`.")
    out = Path(m["_dir"]) / "approved"
    W, H = (int(v) for v in x["kich_thuoc"].split("x"))
    errors, warns, sizes = [], [], {}
    for name in x["files"]:
        p = out / name
        if not p.exists():
            errors.append(f"Thiếu file {name}")
            continue
        sizes[name] = p.stat().st_size // 1024
        if name.endswith(".pptx"):
            continue
        if name.endswith(".pdf"):
            raw = p.read_bytes()
            pages = raw.count(b"/Type /Page") - raw.count(b"/Type /Pages")
            if pages != len(x["trang"]):
                errors.append(f"{name}: {pages} trang, cần {len(x['trang'])}")
            continue
        try:
            im = Image.open(p)
            im.load()
        except Exception as e:  # noqa: BLE001
            errors.append(f"{name}: không mở được ({e})")
            continue
        if im.size != (W, H):
            errors.append(f"{name}: {im.width}×{im.height}, cần {W}×{H}")
        if x.get("trong_suot"):
            if im.mode != "RGBA" or im.getextrema()[3][0] == 255:
                errors.append(f"{name}: yêu cầu nền trong suốt nhưng file không có vùng trong suốt")
        if x.get("max_kb") and sizes[name] > x["max_kb"]:
            warns.append(f"{name}: {sizes[name]}KB > giới hạn {x['max_kb']}KB")
        stem = name.rsplit(".", 1)[0].replace(m["design_id"] + "-", "")
        src = Path(m["_dir"]) / f"v{m['ban_duyet']['v']}" / (f"huong-{m['ban_duyet']['huong']}" if m["ban_duyet"].get("huong") else "") / "out" / f"{stem}.png"
        if src.exists():
            a = Image.open(src).convert("RGB").resize((64, 64))
            bimg = im.convert("RGB").resize((64, 64))
            diff = sum(abs(p1 - p2) for px1, px2 in zip(a.getdata(), bimg.getdata()) for p1, p2 in zip(px1, px2)) / (64 * 64 * 3)
            if diff > 12:
                errors.append(f"{name}: khác bản dựng đã duyệt (sai lệch {diff:.0f}) — có thể bị cắt/vỡ khi nén")
    for need in ("design.json", "source.html", "manifest.json"):
        if not (out / need).exists():
            errors.append(f"Thiếu file nguồn {need}")
    res = {"loi": errors, "canh_bao": warns, "dung_luong_kb": sizes}
    write_json(out / "qa-sau-xuat.json", res)
    m["xuat"]["qa_sau_xuat"] = {"loi": len(errors), "canh_bao": len(warns)}
    save_manifest(m)
    info(f"QA sau xuất {m['design_id']}: " + ("✅ đạt" if not errors else f"❌ {len(errors)} lỗi"))
    for e in errors:
        info(f"  ❌ {e}")
    for w in warns:
        info(f"  ⚠️ {w}")
    info("  Dung lượng: " + ", ".join(f"{k} {v}KB" for k, v in sizes.items()))
    info(f"  Mở xem bằng mắt: {out}/xem-dien-thoai/ (độ dễ đọc trên điện thoại, dấu tiếng Việt, logo)")
    return 1 if errors else 0


def main(cmd, args):
    return export(args) if cmd == "export" else check(args)

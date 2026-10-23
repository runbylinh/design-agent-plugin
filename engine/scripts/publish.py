"""Đưa thành phẩm đã duyệt lên Google Drive — Media Assets / Approved Designs — và ghi nhận link.

  ia drive setup --che-do thu-cong|dong-bo [--sync-root <thư mục Media Assets đã đồng bộ>] [--url <link thư mục Media Assets>] [--id <folder id>]
  ia publish <DS>                    chuẩn bị bộ bàn giao + in việc Claude cần làm với connector Google Drive
  ia link <DS> --url <link thư mục Drive> [--folder-id …] [--kiem '{"tên file": dung_lượng_byte, …}']
                                     ghi link sau khi đã thấy file trên Drive; --kiem đối chiếu tên + dung lượng với bản trên máy

Hai chế độ (đã đo 2026-10-23: connector Google Drive chỉ chở an toàn file nhị phân ~20KB):
  thu-cong (mặc định)  Claude tạo thư mục + ghi design.json/manifest.json qua connector (file chữ), người dùng kéo ảnh vào
                       thư mục đó; Claude tìm lại file để lấy link và đối chiếu dung lượng.
  dong-bo              máy có Google Drive for Desktop: chép thẳng vào thư mục Media Assets đã đồng bộ, Claude chỉ lấy link.
Chưa có link hợp lệ → trạng thái "Chờ upload", KHÔNG báo đã bàn giao. Không đổi quyền chia sẻ của file/thư mục.
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

from common import die, info, log, manifest, now, read_json, save_manifest, save_studio_config, studio_config, warn

SKIP = {"xem-dien-thoai", "qa-sau-xuat.json"}


def opt(args, name, default=None):
    return args[args.index(name) + 1] if name in args else default


def drive_setup(args):
    cfg = studio_config()
    d = cfg.setdefault("drive", {})
    mode = opt(args, "--che-do", d.get("che_do", "thu-cong"))
    if mode not in ("thu-cong", "dong-bo"):
        die("--che-do thu-cong | dong-bo")
    d["che_do"] = mode
    if opt(args, "--sync-root"):
        p = Path(opt(args, "--sync-root")).expanduser()
        if not p.exists():
            die(f"Không thấy {p}. Mở Google Drive for Desktop và chọn đúng thư mục Media Assets.")
        d["sync_root"] = str(p)
    if mode == "dong-bo" and not d.get("sync_root"):
        die("Chế độ dong-bo cần --sync-root <thư mục Media Assets trên máy>.")
    for k in ("url", "id"):
        if opt(args, f"--{k}"):
            d[f"media_assets_{k}"] = opt(args, f"--{k}")
    d.setdefault("thu_muc_thanh_pham", "Approved Designs/{brand}/{thang}/{ds}")
    save_studio_config(cfg)
    info(f"Drive: chế độ {mode}" + (f" · {d.get('sync_root')}" if mode == "dong-bo" else "")
         + (f" · Media Assets {d.get('media_assets_url') or d.get('media_assets_id')}" if d.get("media_assets_url") or d.get("media_assets_id") else ""))
    return 0


def bundle(m):
    src = Path(m["_dir"]) / "approved"
    files = [f for f in sorted(src.iterdir()) if f.name not in SKIP and not f.is_dir()]
    return src, files


def publish(args):
    m = manifest(args[0] if args else die(__doc__))
    x = m.get("xuat") or die("Chưa xuất file (`ia export`).", 2)
    if (x.get("qa_sau_xuat") or {}).get("loi"):
        die("QA sau xuất còn lỗi (`ia check`) — sửa trước khi bàn giao.", 2)
    cfg = studio_config()
    d = cfg.get("drive") or {"che_do": "thu-cong"}
    thang = datetime.now().strftime("%Y-%m")
    job_folder = f"{m['design_id']} · {m['ten']}"[:90].replace("/", "-")
    rel = d.get("thu_muc_thanh_pham", "02 Final/{thang}/{thu_muc}").format(
        brand=(m.get("brand") or "brand").upper(), thang=thang, ds=m["design_id"], thu_muc=job_folder)
    src, files = bundle(m)
    sizes = {f.name: f.stat().st_size for f in files}
    bg = m.get("ban_giao") or {}
    drive = {"che_do": d.get("che_do", "thu-cong"), "thu_muc": rel, "trang_thai": "Chờ upload", "files": sizes, "luc": now()}
    if drive["che_do"] == "dong-bo":
        dest = Path(d["sync_root"]).expanduser() / rel
        dest.mkdir(parents=True, exist_ok=True)
        for f in files:
            shutil.copy2(f, dest / f.name)
        if (src / "assets").exists():
            shutil.copytree(src / "assets", dest / "assets", dirs_exist_ok=True)
        info(f"Đã chép {len(files)} file vào thư mục đồng bộ: {dest}")
        info("Việc của Claude: chờ Drive đồng bộ xong → connector search_files (title = tên file / thư mục "
             f"'{m['design_id']}') → lấy link thư mục → `ia link {m['design_id']} --url <link> --kiem '<tên:dung lượng>'`.")
    else:
        out = Path(m["_dir"]) / "ban-giao"
        if out.exists():
            shutil.rmtree(out)
        out.mkdir()
        for f in files:
            shutil.copy2(f, out / f.name)
        text_files = [f.name for f in files if f.suffix in (".json", ".html", ".md")]
        bin_files = [f.name for f in files if f.name not in text_files]
        info(f"Bộ bàn giao: {out}")
        info("Việc của Claude với connector Google Drive (chế độ thủ công):")
        if d.get("final_id"):
            info(f"  1. Trong thư mục 02 Final (id {d['final_id']}): search_files tìm thư mục '{thang}', chưa có thì create_file (mimeType folder).")
            info(f"     Trong đó tạo thư mục '{job_folder}', bên trong tạo thư mục con '_nguon'.")
        else:
            info(f"  1. Tìm/tạo thư mục '{rel}' (và thư mục con '_nguon') trong Media Assets "
                 f"({d.get('media_assets_url') or 'hỏi người dùng link Media Assets'}) — create_file mimeType folder, từng cấp.")
        info(f"  2. Ghi file chữ vào '_nguon' bằng textContent (không base64), disableConversionToGoogleType=true: {', '.join(text_files)}")
        info(f"  3. Nhờ người dùng kéo {len(bin_files)} file ảnh/PDF từ {out} vào thư mục '{job_folder}' (gửi họ link thư mục):")
        for n in bin_files:
            info(f"       {n}  ({sizes[n] // 1024}KB)")
        info("  4. search_files parentId = <id thư mục việc> và <id _nguon> → so tên + fileSize, rồi:")
        info(f"     ia link {m['design_id']} --url <link thư mục việc> --folder-id <id> --kiem '{{\"tên\": fileSize, …}}' [--source-url <link ảnh thô>]")
    bg["drive"] = drive
    m["ban_giao"] = bg
    m["trang_thai"] = "Chờ upload"
    log(m, f"chuẩn bị bàn giao Drive ({drive['che_do']}): {rel}")
    save_manifest(m)
    import tracker
    tracker.upsert("Viec", m["design_id"], {"Trạng thái": "Chờ upload"})
    tracker.recap(m["design_id"], (m.get("ban_duyet") or {}).get("v"), "Bàn giao", f"Chuẩn bị thư mục {rel} — chờ đưa ảnh lên Drive")
    tracker.hint_push()
    return 0


def link(args):
    m = manifest(args[0] if args else die(__doc__))
    url = opt(args, "--url") or die("Thiếu --url <link thư mục Drive>")
    if "drive.google.com" not in url and "docs.google.com" not in url:
        die("Link không phải Google Drive.")
    drive = (m.get("ban_giao") or {}).get("drive") or die("Chưa chạy `ia publish`.")
    problems = []
    if opt(args, "--kiem"):
        try:
            seen = json.loads(opt(args, "--kiem"))
        except json.JSONDecodeError:
            die("--kiem phải là JSON {\"tên file\": dung_lượng_byte}")
        for name, size in drive["files"].items():
            if name not in seen:
                problems.append(f"chưa thấy {name} trên Drive")
            elif seen[name] not in (None, "") and int(seen[name]) != int(size):
                problems.append(f"{name}: Drive {seen[name]} byte ≠ máy {size} byte (file hỏng/khác bản)")
    else:
        warn("Không có --kiem → chưa đối chiếu được từng file. Nên kiểm tên + dung lượng trên Drive.")
    if problems:
        for p in problems:
            info(f"  ❌ {p}")
        drive["trang_thai"] = "Chờ upload"
        log(m, "đối chiếu Drive chưa đạt: " + "; ".join(problems))
        save_manifest(m)
        return 2
    drive.update({"trang_thai": "Đã upload", "link": url, "folder_id": opt(args, "--folder-id", ""), "xac_nhan_luc": now()})
    m["trang_thai"] = "Đã bàn giao" if not m["nguon"].get("task_id") else "Đã duyệt"
    if opt(args, "--source-url"):
        drive["source_link"] = opt(args, "--source-url")
    log(m, f"đã có link Drive: {url}")
    save_manifest(m)
    import tracker
    fields = {"Link final": url, "Trạng thái": "Đã bàn giao"}
    if drive.get("source_link"):
        fields["Link source thô"] = drive["source_link"]
    tracker.upsert("Viec", m["design_id"], fields)
    tracker.recap(m["design_id"], (m.get("ban_duyet") or {}).get("v"), "Bàn giao", f"Thành phẩm trên Drive: {url}",
                  qa_may=f"Đối chiếu {len(drive['files'])} file trên Drive: khớp" if opt(args, "--kiem") else "Chưa đối chiếu từng file")
    info(f"✅ {m['design_id']}: thành phẩm trên Drive → {url}")
    tracker.hint_push()
    if m["nguon"].get("task_id"):
        info(f"Tiếp: `ia sync {m['design_id']} xuat-thu` để ghi link + trạng thái vào 04 Production ({m['nguon']['task_id']}).")
    return 0


def main(cmd, args):
    if cmd == "drive":
        if not args or args[0] != "setup":
            die(__doc__)
        return drive_setup(args[1:])
    return publish(args) if cmd == "publish" else link(args)

"""ia — lệnh của Agent 02 Ảnh (image-agent). Chạy `ia help`."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

HELP = """ia — Agent 02 Ảnh (dựng ấn phẩm tĩnh theo Brand Kit)

Cài đặt & studio
  ia setup | ia doctor
  ia studio init <thư mục> [--brand-kit <thư mục brand-kit có sẵn> --brand <tên>]
  ia brand show|check [<brand>] · ia brand init <brand> [--tu <thư mục>] · ia brand colors <ảnh…>
  ia font get "<Tên font>" · ia icons install|find <từ>
  ia drive setup --che-do thu-cong|dong-bo [--sync-root …] [--url <Media Assets>]
  ia content connect <workspace Agent Content>

Nhận việc
  ia job new --loai <loại> --ten "…" [--ct CT-…] [--task TASK-…]
  ia brief <TASK-ID> --job DS · ia brief --file brief.md --job DS
  ia asset-list <DS>                Graphic Asset List từ script video
  ia assets find <từ khoá…> · ia assets add|list|scan
  ia sync <DS> nhan|thieu|xuat-thu

Dựng & sửa
  ia presets · ia layouts
  ia cutout <ảnh> [--job DS] · ia inspect <ảnh…> · ia upscale <ảnh>
  ia chart <spec.json> --out x.svg
  ia render <DS> [--v N] [--huong a] · ia render --file design.json --out <thư mục>
  ia version new <DS> [--tu vN] [--huong b] --note "…"
  ia lock <DS>

Duyệt, xuất, bàn giao
  ia approve <DS> --v N [--huong b] --xac-nhan "<lời người dùng>"
  ia export <DS> [--dinh-dang png,jpg,pdf] [--max-kb 500] · ia check <DS>
  ia publish <DS> · ia link <DS> --url <link Drive> --kiem '{…}'
  ia source-check <DS>

Tái sử dụng
  ia resize <DS> --preset <khổ> · ia batch <DS|mẫu> --data rows.json
  ia template save|list|use …

Nghiên cứu mẫu & bố cục riêng
  ia research new --ten "…" [--loai …] · ia research add <RS> <ảnh…> --url … --nguon …
  ia research moodboard|show|done <RS> · ia research list
  ia layout check <file.json> · ia layout save <file.json> --ten <tên> [--tu RS-…] · ia layout rm <tên>

Landing page (HTML)
  ia landing new --ten "…" [--muc-tieu dang-ky|ban-hang|su-kien|gioi-thieu] · ia landing tokens
  ia landing check <LP> [--v N] · ia landing version <LP> --note "…"
  ia landing approve <LP> --v N --xac-nhan "…" · ia landing list

Theo dõi
  ia status [--cho-duyet|--dang-lam|--cho-upload|--tat-ca] · ia job find <từ khoá> · ia job show <DS>

Mã thoát: 0 ok · 1 lỗi · 2 bị chặn bởi quy tắc (đọc thông báo, không lách) · 3 nguồn đã đổi
"""


def studio_init(args):
    import shutil
    from common import PLUGIN, STUDIO_FILE, die, info, write_json
    if not args:
        die("ia studio init <thư mục> [--brand-kit <thư mục> --brand <tên>]")
    d = Path(args[0]).expanduser().resolve()
    if (d / STUDIO_FILE).exists():
        die(f"{d} đã là studio.")
    d.mkdir(parents=True, exist_ok=True)
    (d / "jobs").mkdir(exist_ok=True)
    cfg = {"phien_ban_studio": 1, "brand_kits": {}, "brand_mac_dinh": "", "drive": {"che_do": "thu-cong"}, "content": {}}
    if "--brand-kit" in args:
        bk = Path(args[args.index("--brand-kit") + 1]).expanduser().resolve()
        name = args[args.index("--brand") + 1] if "--brand" in args else bk.name
        if not (bk / "brand.json").exists():
            die(f"{bk} không có brand.json")
        cfg["brand_kits"][name] = str(bk)
        cfg["brand_mac_dinh"] = name
        for sub in ("mau", "thanh-phan", "anh-mau"):
            (bk / sub).mkdir(exist_ok=True)
    write_json(d / STUDIO_FILE, cfg)
    shutil.copy2(PLUGIN / "templates" / "studio" / "CLAUDE.md", d / "CLAUDE.md")
    info(f"✅ Đã tạo studio ảnh: {d}" + (f" · Brand Kit {cfg['brand_mac_dinh']}" if cfg["brand_mac_dinh"] else ""))
    return 0


def doctor(args):
    from common import RUNTIME, info
    ok = True
    def line(good, msg):
        nonlocal ok
        ok &= good
        info(("✅ " if good else "❌ ") + msg)
    line(sys.version_info >= (3, 10), f"Python {sys.version.split()[0]} ({sys.executable})")
    for mod, why in (("PIL", "Pillow — xử lý ảnh"), ("playwright", "Playwright — xuất ảnh"), ("rembg", "rembg — tách nền")):
        try:
            __import__(mod)
            line(True, why)
        except ImportError:
            line(False, why + " — chạy `ia setup`")
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch()
            b.close()
        line(True, "Chromium chạy được")
    except Exception as e:  # noqa: BLE001
        line(False, f"Chromium: {str(e).splitlines()[0][:120]} — chạy `ia setup`")
    fonts = list((RUNTIME / "fonts").rglob("*.ttf"))
    line(bool(fonts), f"Font: {len(fonts)} file trong {RUNTIME / 'fonts'}")
    icons = list((RUNTIME / "icons").glob("*.svg"))
    line(len(icons) > 100, f"Biểu tượng: {len(icons)}")
    models = list((RUNTIME / "models").rglob("*.onnx"))
    info(f"ℹ️ Model tách nền đã tải: {', '.join(m.stem for m in models) or 'chưa (tự tải lần đầu)'}")
    return 0 if ok else 1


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("help", "-h", "--help"):
        print(HELP)
        return 0
    cmd, rest = args[0], args[1:]
    if cmd == "doctor":
        return doctor(rest)
    if cmd == "studio":
        if rest[:1] != ["init"]:
            print(HELP)
            return 1
        return studio_init(rest[1:])
    if cmd == "brand":
        import brand
        return brand.main(rest)
    if cmd in ("font", "icons", "assets"):
        import assets
        return assets.main(cmd, rest)
    if cmd in ("job", "version", "approve", "status", "lock"):
        import job
        return job.main(cmd, rest)
    if cmd == "render":
        import render
        return render.main(rest)
    if cmd in ("export", "check"):
        import export
        return export.main(cmd, rest)
    if cmd == "sheet":
        import tracker
        return tracker.main(rest)
    if cmd in ("cutout", "upscale", "inspect"):
        import cutout
        return cutout.main(cmd, rest)
    if cmd == "chart":
        import chart
        return chart.main(rest)
    if cmd in ("content", "brief", "source-check", "asset-list", "sync"):
        import content
        return content.main(cmd, rest)
    if cmd in ("drive", "publish", "link"):
        import publish
        return publish.main(cmd, rest)
    if cmd in ("resize", "batch", "template", "layouts", "presets"):
        import adapt
        return adapt.main(cmd, rest)
    if cmd in ("research", "layout", "landing"):
        import web
        return web.main(cmd, rest)
    print(f"Không có lệnh '{cmd}'.\n{HELP}")
    return 1


if __name__ == "__main__":
    sys.exit(main() or 0)

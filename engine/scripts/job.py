"""Job thiết kế (DS ID), phiên bản, duyệt, tìm lại việc cũ.

  ia job new --loai <thumbnail|carousel|facebook|quang_cao|poster|anh_bia|bieu_do|video_graphic|story>
             --ten "<tên ngắn>" [--brand rbl] [--ct CT-…] [--task TASK-…] [--che-do truc_tiep|content_brief|video_script]
  ia job show <DS>                       toàn bộ manifest (JSON)
  ia job find <từ khoá | CT-… | TASK-…>  tìm job cũ theo tên, mã Content, mã phiếu
  ia version new <DS> [--tu vN] [--huong b] [--note "…"]   tạo phiên bản mới (chép design.json của bản trước / hướng đã chọn)
  ia approve <DS> --v N [--huong b] --xac-nhan "<lời người dùng>"   ghi nhận bản được duyệt (CHỈ sau khi người dùng đồng ý)
  ia status [--cho-duyet | --dang-lam | --cho-upload | --tat-ca]   việc đang dở, chờ duyệt, chờ upload
  ia lock <DS> [--reset --xac-nhan "…"]  xem / đặt lại mốc chữ khoá (khi nội dung nguồn đã được duyệt lại)
"""
import json
import shutil
from datetime import datetime
from pathlib import Path

from common import (die, find_studio, info, log, manifest, now, read_json, save_manifest, slug, studio_config,
                    version_dir, warn, write_json)

LOAI = ["thumbnail", "carousel", "facebook", "anh_don", "quang_cao", "poster", "anh_bia", "bieu_do", "video_graphic", "story"]
STATUS_ORDER = ["Cần sửa", "Chờ duyệt", "Đang làm", "Mới", "Đã duyệt", "Chờ upload", "Đã bàn giao", "Tạm dừng"]


def opt(args, name, default=None):
    return args[args.index(name) + 1] if name in args and args.index(name) + 1 < len(args) else default


def new(args):
    st = find_studio()
    cfg = studio_config(st)
    loai = opt(args, "--loai") or die("Thiếu --loai (" + ", ".join(LOAI) + ")")
    if loai not in LOAI:
        die(f"--loai '{loai}' không hợp lệ. Chọn: {', '.join(LOAI)}")
    ten = opt(args, "--ten") or die("Thiếu --ten")
    brand = opt(args, "--brand", cfg.get("brand_mac_dinh"))
    ymd = datetime.now().strftime("%y%m%d")
    (st / "jobs").mkdir(exist_ok=True)
    n = 1 + max([int(p.name.split("-")[-1]) for p in (st / "jobs").glob(f"DS-{ymd}-*")] or [0])
    did = f"DS-{ymd}-{n:02d}"
    d = st / "jobs" / did
    for sub in ("input", "assets", "v1"):
        (d / sub).mkdir(parents=True)
    import presets
    m = {
        "design_id": did, "ten": ten, "loai": loai, "brand": brand,
        "nguon": {"che_do": opt(args, "--che-do", "content_brief" if opt(args, "--task") or opt(args, "--ct") else "truc_tiep"),
                  "content_id": opt(args, "--ct", ""), "task_id": opt(args, "--task", "")},
        "trang_thai": "Mới", "phien_ban_hien_tai": 1,
        "phien_ban": [{"v": 1, "tao": now(), "ghi_chu": "bản đầu", "trang_thai": "Chưa dựng"}],
        "ban_duyet": None, "xuat": None, "ban_giao": None, "tai_nguyen": [], "noi_dung_khoa": {}, "nhat_ky": [],
        "tao": now(),
    }
    log(m, "tạo job")
    write_json(d / "manifest.json", m)
    design = {"design_id": did, "brand": brand, "output_type": loai,
              "content_id": m["nguon"]["content_id"], "canvas": {"preset": presets.TYPE_DEFAULT.get(loai, "facebook_4x5")},
              "pages": [{"id": "p1", "elements": []}]}
    write_json(d / "v1" / "design.json", design)
    info(f"Đã tạo {did} — {ten}  ({d})")
    info(f"Soạn {d}/v1/design.json rồi `ia render {did}`.")
    print(did)


def show(args):
    m = manifest(args[0] if args else die("ia job show <DS>"))
    m.pop("_dir", None)
    print(json.dumps(m, ensure_ascii=False, indent=2))


def all_jobs(st=None):
    st = st or find_studio()
    out = []
    for f in sorted((st / "jobs").glob("DS-*/manifest.json")):
        m = read_json(f)
        m["_dir"] = str(f.parent)
        out.append(m)
    return out


def find(args):
    q = " ".join(args).lower().strip() or die("ia job find <từ khoá>")
    hits = []
    for m in all_jobs():
        hay = " ".join([m["design_id"], m.get("ten", ""), m["nguon"].get("content_id", ""), m["nguon"].get("task_id", ""),
                        m.get("loai", "")]).lower()
        if all(w in hay or w in slug(hay) for w in q.split()):
            hits.append(m)
    if not hits:
        info("Không thấy job nào khớp.")
    for m in hits:
        line(m)


def line(m):
    bd = m.get("ban_duyet") or {}
    link = ((m.get("ban_giao") or {}).get("drive") or {}).get("link", "")
    info(f"{m['design_id']}  [{m['trang_thai']}]  {m['ten']}  · {m['loai']}"
         f"{' · ' + m['nguon']['content_id'] if m['nguon'].get('content_id') else ''}"
         f"{' · ' + m['nguon']['task_id'] if m['nguon'].get('task_id') else ''}"
         f"  · v{m['phien_ban_hien_tai']}{' (duyệt v' + str(bd['v']) + ')' if bd else ''}"
         f"{'  · ' + link if link else ''}  · cập nhật {m.get('cap_nhat', m.get('tao'))}")


def status(args):
    jobs = all_jobs()
    if not jobs:
        info("Chưa có job nào.")
        return
    filt = {"--cho-duyet": ["Chờ duyệt"], "--dang-lam": ["Mới", "Đang làm", "Cần sửa"], "--cho-upload": ["Chờ upload"]}
    keep = None
    for k, v in filt.items():
        if k in args:
            keep = v
    groups = {}
    for m in jobs:
        if keep and m["trang_thai"] not in keep:
            continue
        if not keep and "--tat-ca" not in args and m["trang_thai"] == "Đã bàn giao":
            continue
        groups.setdefault(m["trang_thai"], []).append(m)
    for s in STATUS_ORDER + sorted(set(groups) - set(STATUS_ORDER)):
        if groups.get(s):
            info(f"\n■ {s} ({len(groups[s])})")
            for m in sorted(groups[s], key=lambda x: x.get("cap_nhat", ""), reverse=True):
                line(m)
    done = sum(1 for m in jobs if m["trang_thai"] == "Đã bàn giao")
    if done and "--tat-ca" not in args and not keep:
        info(f"\n(+{done} job đã bàn giao — thêm --tat-ca để xem)")


def version_new(args):
    m = manifest(args[0] if args else die("ia version new <DS>"))
    src_v = int(str(opt(args, "--tu", f"v{m['phien_ban_hien_tai']}")).lstrip("v"))
    huong = opt(args, "--huong")
    src = version_dir(m, src_v) / (f"huong-{huong}" if huong else "") / "design.json"
    if not src.exists():
        die(f"Không thấy {src}")
    nv = max(x["v"] for x in m["phien_ban"]) + 1
    nd = Path(m["_dir"]) / f"v{nv}"
    nd.mkdir()
    shutil.copy2(src, nd / "design.json")
    note = opt(args, "--note", f"từ v{src_v}{' hướng ' + huong if huong else ''}")
    m["phien_ban"].append({"v": nv, "tao": now(), "ghi_chu": note, "tu": f"v{src_v}{'/' + huong if huong else ''}", "trang_thai": "Chưa dựng"})
    m["phien_ban_hien_tai"] = nv
    if m["trang_thai"] in ("Chờ duyệt", "Đã duyệt", "Mới"):
        m["trang_thai"] = "Đang làm"
    log(m, f"tạo v{nv}: {note}")
    save_manifest(m)
    info(f"Đã tạo v{nv} ({note}) → {nd}/design.json")


def approve(args):
    m = manifest(args[0] if args else die("ia approve <DS> --v N --xac-nhan \"…\""))
    v = int(str(opt(args, "--v") or die("Thiếu --v")).lstrip("v"))
    xn = opt(args, "--xac-nhan") or die("Thiếu --xac-nhan \"<lời người dùng đồng ý>\" — chỉ duyệt khi người dùng đã nói đồng ý trong chat.")
    huong = opt(args, "--huong")
    vd = version_dir(m, v) / (f"huong-{huong}" if huong else "")
    qa = read_json(vd / "qa.json", {})
    if not qa:
        die(f"v{v}{' hướng ' + huong if huong else ''} chưa dựng (`ia render {m['design_id']} --v {v}`).")
    if qa.get("loi") and "--chap-nhan-loi" not in args:
        die(f"v{v} còn {len(qa['loi'])} lỗi chặn trong qa.json. Sửa trước, hoặc người dùng chấp nhận rõ ràng → thêm --chap-nhan-loi.", 2)
    m["ban_duyet"] = {"v": v, "huong": huong, "luc": now(), "xac_nhan": xn}
    m["trang_thai"] = "Đã duyệt"
    log(m, f"duyệt v{v}{' hướng ' + huong if huong else ''}: \"{xn}\"")
    save_manifest(m)
    info(f"✅ {m['design_id']} duyệt v{v}. Tiếp: `ia export {m['design_id']}`.")


def lock(args):
    m = manifest(args[0] if args else die("ia lock <DS>"))
    if "--reset" in args:
        xn = opt(args, "--xac-nhan") or die("Đặt lại chữ khoá cần --xac-nhan \"<lời người dùng / bản nguồn mới đã duyệt>\"")
        m["noi_dung_khoa"] = {}
        log(m, f"đặt lại mốc chữ khoá: \"{xn}\" — lần dựng kế tiếp lấy làm mốc mới")
        save_manifest(m)
        info("Đã xoá mốc chữ khoá. Lần `ia render` tới sẽ ghi mốc mới.")
        return
    for k, v in (m.get("noi_dung_khoa") or {}).items():
        info(f"  {k}: {v}")
    if not m.get("noi_dung_khoa"):
        info("Chưa có mốc (ghi ở lần dựng đầu tiên).")


def main(cmd, args):
    if cmd == "job":
        if not args:
            die(__doc__)
        sub, rest = args[0], args[1:]
        {"new": new, "show": show, "find": find}.get(sub, lambda a: die(__doc__))(rest)
    elif cmd == "version":
        if not args or args[0] != "new":
            die(__doc__)
        version_new(args[1:])
    elif cmd == "approve":
        approve(args)
    elif cmd == "status":
        status(args)
    elif cmd == "lock":
        lock(args)
    return 0

"""Tái sử dụng: đổi kích thước (dàn lại bố cục), nhân bản từ mẫu, thư viện mẫu đã duyệt.

  ia resize <DS> --preset <khổ> [--layout <bố cục>] [--ten "…"]   job mới cùng nội dung, khổ mới (D06)
  ia batch <DS | tên mẫu> --data rows.json                          nhiều job từ một mẫu, mỗi dòng một bộ nội dung (D08)
        rows.json: [{"ten": "Chủ đề 1", "noi_dung": {"headline": "…", "sub": "…"}, "anh": {"subject": "assets/a.png"}}, …]
  ia template save <DS> --ten <tên-mau> [--cho-doi id1,id2] [--mo-ta "…"]   lưu bản đã duyệt vào Brand Kit/mau/ (thư viện mẫu)
  ia template list
  ia template use <tên-mau> --ten "…" [--loai …] [--ct CT-…]              job mới từ mẫu
  ia layouts                                                          các bố cục có sẵn + biến thể tỉ lệ
  ia presets                                                          các khổ chuẩn + vùng an toàn
"""
import copy
import json
import shutil
from pathlib import Path

import brand as brandmod
import job as jobmod
import presets
from common import die, find_studio, info, log, manifest, now, read_json, save_manifest, slug, studio_config, version_dir, warn, write_json
from compose import LAYOUT_DIR


def opt(args, name, default=None):
    return args[args.index(name) + 1] if name in args else default


def _approved_design(m):
    bd = m.get("ban_duyet")
    if not bd:
        warn(f"{m['design_id']} chưa duyệt — dùng phiên bản hiện tại v{m['phien_ban_hien_tai']}.")
        return read_json(version_dir(m) / "design.json")
    return read_json(version_dir(m, bd["v"]) / (f"huong-{bd['huong']}" if bd.get("huong") else "") / "design.json")


def _new_job_from(design, loai, ten, src_m=None, extra=None):
    import io
    import contextlib
    buf = io.StringIO()
    args = ["--loai", loai, "--ten", ten, "--brand", design.get("brand") or ""]
    if src_m and src_m["nguon"].get("content_id"):
        args += ["--ct", src_m["nguon"]["content_id"]]
    if src_m and src_m["nguon"].get("task_id"):
        args += ["--task", src_m["nguon"]["task_id"]]
    with contextlib.redirect_stdout(buf):
        jobmod.new(args)
    did = buf.getvalue().strip().splitlines()[-1]
    m = manifest(did)
    d = copy.deepcopy(design)
    d["design_id"] = did
    if extra:
        d.update(extra)
    write_json(version_dir(m, 1) / "design.json", d)
    # chép tài nguyên của job gốc
    if src_m and (Path(src_m["_dir"]) / "assets").exists():
        shutil.copytree(Path(src_m["_dir"]) / "assets", Path(m["_dir"]) / "assets", dirs_exist_ok=True)
    if src_m:
        m["nguon"].update({k: v for k, v in src_m["nguon"].items() if k.startswith("hash") or k in ("ban_nguon", "tham_chieu", "chu_da_duyet")})
        m["goc"] = src_m["design_id"]
        m["noi_dung_khoa"] = dict(src_m.get("noi_dung_khoa") or {})
        log(m, f"tạo từ {src_m['design_id']}")
        save_manifest(m)
    return did, m


def resize(args):
    src = manifest(args[0] if args else die(__doc__))
    pre = opt(args, "--preset") or die("Thiếu --preset (xem `ia presets`).")
    try:
        p = presets.get(pre)
    except KeyError:
        die(f"Không có khổ '{pre}'.")
    d = _approved_design(src)
    old = d.get("canvas", {})
    d["canvas"] = {"preset": pre}
    if opt(args, "--layout"):
        d["layout"] = opt(args, "--layout")
    fixed = []
    for pg in d.get("pages", [{"elements": d.get("elements", [])}]):
        if opt(args, "--layout"):
            pg.pop("layout", None)
        for el in pg.get("elements", []):
            b = el.get("box")
            if b:
                fixed.append(el.get("id"))
            if b and not all(isinstance(v, (int, float)) and 0 <= v <= 1 for v in b):
                ow, oh = old.get("w") or presets.get(old.get("preset", pre))["w"], old.get("h") or presets.get(old.get("preset", pre))["h"]
                el["box"] = [round(b[0] / ow, 4), round(b[1] / oh, 4), round(b[2] / ow, 4), round(b[3] / oh, 4)]
    loai = opt(args, "--loai", src.get("loai"))
    did, m = _new_job_from(d, loai, opt(args, "--ten", f"{src['ten']} · {p['ten']}"), src)
    info(f"Đã tạo {did}: {p['ten']} ({p['w']}×{p['h']}) từ {src['design_id']}.")
    if fixed:
        warn("Các thành phần đặt vị trí cố định (box) chỉ được đổi theo tỉ lệ, chưa dàn lại: " + ", ".join(fixed)
             + " — sửa box hoặc chuyển sang vùng (slot) của bố cục, rồi dựng lại.")
    info(f"Dựng: `ia render {did}` → mở ảnh kiểm: chữ vẫn đọc được, chủ thể không bị cắt, đúng vùng an toàn khổ mới.")
    return 0


def batch(args):
    if not args or "--data" not in args:
        die(__doc__)
    src_key = args[0]
    if src_key.startswith("DS-"):
        sm = manifest(src_key)
        base = _approved_design(sm)
        loai = sm["loai"]
    else:
        b = brandmod.load()
        f = Path(b["dir"]) / "mau" / f"{src_key}.json"
        if not f.exists():
            die(f"Không có mẫu '{src_key}' trong {Path(b['dir']) / 'mau'}.")
        tpl = read_json(f)
        base, loai, sm = tpl["design"], tpl.get("loai", "facebook"), None
        allowed = set(tpl.get("cho_doi", []))
    rows = read_json(opt(args, "--data"))
    made = []
    for i, row in enumerate(rows, 1):
        d = copy.deepcopy(base)
        changed = set()
        for pg in d.get("pages", []):
            for el in pg.get("elements", []):
                eid = el.get("id")
                if eid in row.get("noi_dung", {}):
                    if el.get("type") == "list":
                        el["items"] = row["noi_dung"][eid]
                    else:
                        el["content"] = row["noi_dung"][eid]
                    changed.add(eid)
                if eid in row.get("anh", {}):
                    el["src"] = row["anh"][eid]
                    changed.add(eid)
        if not sm and allowed and changed - allowed:
            die(f"Dòng {i}: mẫu chỉ cho đổi {sorted(allowed)}, đang đổi cả {sorted(changed - allowed)}.")
        missing = set(row.get("noi_dung", {})) | set(row.get("anh", {}))
        missing -= changed
        if missing:
            warn(f"Dòng {i}: không có thành phần {sorted(missing)} trong mẫu.")
        did, m = _new_job_from(d, loai, row.get("ten", f"Bản {i}"), sm)
        m["noi_dung_khoa"] = {}                       # nội dung mới → mốc khoá mới ở lần dựng đầu
        m["goc"] = src_key
        save_manifest(m)
        made.append(did)
    info(f"Đã tạo {len(made)} job từ {src_key}: {', '.join(made)}")
    info("Dựng từng job (`ia render <DS>`), xem ảnh, trình người dùng duyệt theo lô.")
    return 0


def template(args):
    if not args:
        die(__doc__)
    act = args[0]
    b = brandmod.load()
    mau = Path(b["dir"]) / "mau"
    mau.mkdir(exist_ok=True)
    if act == "save":
        m = manifest(args[1])
        if not m.get("ban_duyet"):
            die("Chỉ lưu mẫu từ bản đã duyệt.", 2)
        ten = slug(opt(args, "--ten") or die("Thiếu --ten"))
        d = _approved_design(m)
        tpl = {"ten": ten, "mo_ta": opt(args, "--mo-ta", m["ten"]), "loai": m["loai"], "tu": m["design_id"], "luc": now(),
               "cho_doi": [x for x in (opt(args, "--cho-doi", "") or "").split(",") if x], "design": d}
        write_json(mau / f"{ten}.json", tpl)
        out = Path(m["_dir"]) / "approved"
        prev = next(iter(sorted(out.glob("*.png"))), None)
        if prev:
            shutil.copy2(prev, mau / f"{ten}.png")
        info(f"Đã lưu mẫu '{ten}' vào {mau}. Được đổi: {', '.join(tpl['cho_doi']) or '(chưa khai báo — mọi chữ/ảnh)'}")
    elif act == "list":
        for f in sorted(mau.glob("*.json")):
            t = read_json(f)
            info(f"{f.stem:28s} [{t.get('loai')}] {t.get('mo_ta', '')} · đổi được: {', '.join(t.get('cho_doi', [])) or 'mọi chữ/ảnh'}")
    elif act == "use":
        ten = args[1] if len(args) > 1 else die("ia template use <tên-mau> --ten …")
        f = mau / f"{ten}.json"
        if not f.exists():
            die(f"Không có mẫu '{ten}'.")
        t = read_json(f)
        did, m = _new_job_from(t["design"], opt(args, "--loai", t.get("loai", "facebook")), opt(args, "--ten", ten))
        if opt(args, "--ct"):
            m["nguon"]["content_id"] = opt(args, "--ct")
        m["goc"] = f"mau:{ten}"
        save_manifest(m)
        info(f"Đã tạo {did} từ mẫu '{ten}'. Thay nội dung trong v1/design.json (chỉ các thành phần mẫu cho đổi), rồi `ia render {did}`.")
    else:
        die(__doc__)
    return 0


def layouts(args):
    for f in sorted(LAYOUT_DIR.glob("*.json")):
        lay = read_json(f)
        regions = sorted({r for v in lay.get("variants", {}).values() for r in v.get("regions", {})})
        info(f"{f.stem:26s} {', '.join(lay.get('variants', {}))}  · {lay.get('mo_ta', '')}\n{'':26s} vùng: {', '.join(regions)}")
    return 0


def main(cmd, args):
    if cmd == "presets":
        info(presets.table())
        return 0
    return {"resize": resize, "batch": batch, "template": template, "layouts": layouts}[cmd](args)

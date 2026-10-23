"""Cầu nối Agent 01 Content: đọc phiếu 04 Production, chuẩn hoá Brief, khoá phiên bản nguồn, cập nhật trạng thái.

  ia content connect <thư mục workspace content> [--sheet <đường dẫn bin/sheet>]   ghi nhớ workspace Agent Content
  ia content <lệnh sheet…>          chạy lệnh `sheet` của content-agent trong đúng workspace (vd: ia content get Production "Agent phụ trách=Agent 02 – Ảnh")
  ia brief <TASK-ID> [--job DS]     đọc phiếu → input/brief.json (chữ đã duyệt theo trang/cảnh + mã băm từng phần)
  ia brief --file <brief.md|script.md> [--job DS]   Brief/Script dán tay (giao việc trực tiếp)
  ia source-check <DS>              so nguồn hiện tại với mã băm đã khoá → phần nào đổi, đồ hoạ nào bị ảnh hưởng (D15)
  ia asset-list <DS>                lập Graphic Asset List từ script video (D14) → input/asset-list.json để người dùng duyệt
  ia sync <DS> nhan|thieu|xuat-thu [--note "…"]   cập nhật phiếu: Đang thực hiện / Thiếu tư liệu / Đã xuất file thử + link

Agent 02 chỉ chuyển phiếu tới "Đã xuất file thử". QA, Đạt QA, Hoàn thành, Duyệt 04 là việc của Agent 01 + người dùng.
"""
import glob
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from common import (die, info, log, manifest, now, read_json, save_manifest, save_studio_config, studio_config, text_hash,
                    warn, write_json, norm_text)

PART_RE = re.compile(r"^\s*\[?\s*(Trang|Cảnh|Canh|Slide|SC)[\s\-]*(\d+)\s*\]?\s*[:|\]]?\s*(.*)$", re.I)
SCENE_ID_RE = re.compile(r"\b(SC-\d{2,3})\b")
GRAPHIC_HINTS = ["biểu đồ", "sơ đồ", "số liệu", "bảng", "so sánh", "danh sách", "ý chính", "cta", "tiêu đề", "hook", "phễu",
                 "chữ màn hình", "text màn hình", "thẻ", "infographic", "timeline", "quy trình", "bước"]


def opt(args, name, default=None):
    return args[args.index(name) + 1] if name in args else default


def sheet_bin(cfg):
    c = cfg.get("content") or {}
    if c.get("sheet") and Path(c["sheet"]).exists():
        return c["sheet"]
    env = os.environ.get("CONTENT_AGENT_SHEET")
    if env and Path(env).exists():
        return env
    cands = glob.glob(str(Path.home() / ".claude/plugins/cache/*/content-agent/*/bin/sheet"))
    if not cands:
        return None
    def ver(p):
        return tuple(int(x) for x in re.findall(r"\d+", Path(p).parts[-3])[:3])
    return sorted(cands, key=ver)[-1]


def run_sheet(args, cfg=None, check=True):
    cfg = cfg or studio_config()
    sb = sheet_bin(cfg)
    ws = (cfg.get("content") or {}).get("workspace")
    if not sb:
        die("Không thấy plugin content-agent (lệnh sheet). Cài content-agent hoặc `ia content connect <workspace> --sheet <đường dẫn bin/sheet>`.")
    if not ws:
        die("Chưa nối workspace Agent Content. Chạy `ia content connect <thư mục có content-studio.json>`.")
    env = dict(os.environ, CONTENT_STUDIO=ws, PYTHONIOENCODING="utf-8")
    r = subprocess.run([sys.executable, sb, *args], capture_output=True, text=True, encoding="utf-8", env=env, cwd=ws)
    if check and r.returncode != 0:
        die(f"sheet {' '.join(args)} → {(r.stderr or r.stdout).strip()}", r.returncode)
    return r


def connect(args):
    cfg = studio_config()
    ws = Path(args[0]).expanduser().resolve() if args else die("ia content connect <thư mục workspace>")
    if not (ws / "content-studio.json").exists():
        die(f"{ws} không phải workspace Agent Content (thiếu content-studio.json).")
    c = cfg.setdefault("content", {})
    c["workspace"] = str(ws)
    if opt(args, "--sheet"):
        c["sheet"] = str(Path(opt(args, "--sheet")).expanduser().resolve())
    save_studio_config(cfg)
    sb = sheet_bin(cfg)
    info(f"Đã nối workspace Agent Content: {ws}\nLệnh sheet: {sb or 'CHƯA THẤY — cài content-agent'}")
    if sb:
        r = run_sheet(["info"], cfg, check=False)
        info(r.stdout.strip()[:800])
    return 0


# ------------------------------------------------------------------ Brief

def split_parts(text):
    """Tách chữ theo Trang n / Cảnh n / SC-xx. Trả [(key, scene_id, nội dung)]."""
    parts, cur = [], None
    for line in (text or "").splitlines():
        mt = PART_RE.match(line)
        if mt:
            kind = mt.group(1).lower()
            num = int(mt.group(2))
            sid = SCENE_ID_RE.search(line)
            key = sid.group(1) if sid else (f"SC-{num:02d}" if kind == "sc" else (f"Trang {num}" if kind in ("trang", "slide") else f"Cảnh {num}"))
            cur = [key, bool(sid) or kind == "sc", [mt.group(3)]]
            parts.append(cur)
        elif cur is not None:
            cur[2].append(line)
    return [(k, stable, "\n".join(x for x in lines).strip()) for k, stable, lines in parts]


def normalize(row, src_label):
    text = row.get("Hook / Caption / Kịch bản", "") or ""
    brief = row.get("Brief ảnh / video", "") or ""
    parts = split_parts(text) or split_parts(brief)
    loai = row.get("Loại nhiệm vụ", "")
    is_video = loai in ("Dựng video",) or bool(re.search(r"\[(Cảnh|Canh)\s*\d", text + brief, re.I)) or "BRIEF VIDEO" in brief.upper()
    out = {
        "nguon": src_label, "doc_luc": now(),
        "task_id": row.get("Task ID", ""), "content_id": row.get("Content ID", ""), "loai_nhiem_vu": loai,
        "kenh": row.get("Kênh", ""), "format": row.get("Format", ""), "kich_thuoc": row.get("Kích thước / tỷ lệ", ""),
        "han": row.get("Hạn hoàn thành", ""), "tu_lieu": row.get("Link tư liệu / Brand Kit", ""),
        "trang_thai_duyet_chu": row.get("Trạng thái duyệt chữ", ""), "phien_ban": row.get("Phiên bản", ""),
        "chu_da_duyet": text, "brief": brief, "la_script_video": is_video,
        "phan": [{"key": k, "scene_id_on_dinh": stable, "noi_dung": c, "hash": text_hash(c)} for k, stable, c in parts],
        "hash_tong": text_hash(text + "\n" + brief),
    }
    if is_video and out["phan"] and not all(p["scene_id_on_dinh"] for p in out["phan"]):
        out["canh_bao"] = ("Script chưa có Scene ID cố định (SC-01…). Đồ hoạ sẽ gắn theo số thứ tự cảnh — nếu Agent 01 chèn/xoá cảnh, "
                           "đối chiếu thay đổi sẽ kém chính xác. Đề nghị Agent 01 ghi Scene ID.")
    return out


def brief(args):
    if "--file" in args:
        f = Path(opt(args, "--file")).expanduser()
        txt = f.read_text(encoding="utf-8")
        row = {"Hook / Caption / Kịch bản": txt, "Brief ảnh / video": txt if "BRIEF" in txt.upper() else "",
               "Trạng thái duyệt chữ": "Người dùng giao trực tiếp", "Loại nhiệm vụ": ""}
        data = normalize(row, f"file:{f}")
    else:
        tid = args[0] if args and not args[0].startswith("--") else die(__doc__)
        r = run_sheet(["show", tid])
        try:
            row = json.loads(r.stdout)
        except json.JSONDecodeError:
            die(f"Không đọc được phiếu {tid}:\n{r.stdout[:600]}")
        data = normalize(row, f"sheet:{tid}")
        if row.get("Agent phụ trách") and "Ảnh" not in row.get("Agent phụ trách", "") and "Video" not in row.get("Agent phụ trách", ""):
            warn(f"Phiếu {tid} giao cho '{row.get('Agent phụ trách')}', không phải Agent 02 – Ảnh.")
        if data["trang_thai_duyet_chu"] != "Đã duyệt":
            warn(f"Chữ của {tid} chưa duyệt (Trạng thái duyệt chữ = '{data['trang_thai_duyet_chu']}') → chỉ làm bản THỬ, "
                 "không coi là lệnh sản xuất chính thức.")
    job = opt(args, "--job")
    if job:
        m = manifest(job)
        write_json(Path(m["_dir"]) / "input" / "brief.json", data)
        n = m["nguon"]
        n.update({"content_id": data["content_id"] or n.get("content_id", ""), "task_id": data["task_id"] or n.get("task_id", ""),
                  "ban_nguon": data["phien_ban"], "hash_tong": data["hash_tong"], "hash_phan": {p["key"]: p["hash"] for p in data["phan"]},
                  "chu_da_duyet": data["trang_thai_duyet_chu"] == "Đã duyệt", "doc_luc": data["doc_luc"], "tham_chieu": data["nguon"]})
        if data["la_script_video"]:
            n["che_do"] = "video_script"
        log(m, f"nhận Brief từ {data['nguon']} ({len(data['phan'])} phần, mã {data['hash_tong']})")
        save_manifest(m)
        info(f"Đã lưu {Path(m['_dir']) / 'input' / 'brief.json'}")
    print(json.dumps({k: v for k, v in data.items() if k not in ("chu_da_duyet", "brief")}, ensure_ascii=False, indent=2))
    if data.get("canh_bao"):
        warn(data["canh_bao"])
    return 0


def source_check(args):
    m = manifest(args[0] if args else die("ia source-check <DS>"))
    n = m["nguon"]
    ref = n.get("tham_chieu", "")
    if not n.get("hash_tong"):
        die("Job này chưa khoá nguồn (chưa chạy `ia brief … --job`).")
    if ref.startswith("sheet:"):
        r = run_sheet(["show", ref[6:]])
        cur = normalize(json.loads(r.stdout), ref)
    elif ref.startswith("file:"):
        f = Path(ref[5:])
        txt = f.read_text(encoding="utf-8")
        cur = normalize({"Hook / Caption / Kịch bản": txt, "Brief ảnh / video": ""}, ref)
    else:
        die("Không biết nguồn để đối chiếu.")
    if cur["hash_tong"] == n["hash_tong"]:
        info(f"✅ Nguồn {ref} không đổi so với lúc nhận việc ({n.get('doc_luc')}).")
        return 0
    old = n.get("hash_phan", {})
    new = {p["key"]: p["hash"] for p in cur["phan"]}
    changed = [k for k in new if k in old and new[k] != old[k]]
    added = [k for k in new if k not in old]
    removed = [k for k in old if k not in new]
    info(f"⚠️ Nguồn đã đổi (bản cũ {n.get('ban_nguon') or '—'} → hiện tại {cur['phien_ban'] or '—'}).")
    for lab, ks in (("Sửa", changed), ("Thêm", added), ("Bỏ", removed)):
        if ks:
            info(f"  {lab}: {', '.join(ks)}")
    if not (changed or added or removed):
        info("  Phần Brief/chữ chung đổi (không tách được theo trang/cảnh) → rà lại toàn bộ.")
    al = m.get("asset_list") or []
    hit = [a for a in al if a.get("scene") in changed + removed]
    if hit:
        info("  Đồ hoạ bị ảnh hưởng: " + ", ".join(f"{a['id']} ({a['scene']})" for a in hit))
    info("Không tự thay file đã duyệt/đã bàn giao. Đề xuất cho người dùng: giữ đồ hoạ không đổi, sửa phần đổi, thêm/bỏ theo nguồn mới → bản mới để duyệt.")
    m.setdefault("canh_bao_nguon", []).append({"luc": now(), "sua": changed, "them": added, "bo": removed, "hash_moi": cur["hash_tong"]})
    log(m, f"phát hiện nguồn đổi: sửa {changed}, thêm {added}, bỏ {removed}")
    save_manifest(m)
    return 3


def asset_list(args):
    m = manifest(args[0] if args else die("ia asset-list <DS>"))
    b = read_json(Path(m["_dir"]) / "input" / "brief.json", {}) or die("Chưa có input/brief.json — chạy `ia brief … --job`.")
    items = []
    for i, p in enumerate(b.get("phan", []), 1):
        low = p["noi_dung"].lower()
        hints = [h for h in GRAPHIC_HINTS if h in low]
        screen = re.search(r"chữ (màn hình|trên màn hình)\s*:\s*([^|\n]+)", p["noi_dung"], re.I)
        if not hints and not screen:
            continue
        kind = ("bieu_do" if any(h in low for h in ("biểu đồ", "số liệu", "bảng", "phễu")) else
                "so_do" if any(h in low for h in ("sơ đồ", "quy trình", "bước", "timeline")) else
                "cta" if "cta" in low else "the_chu")
        items.append({"id": f"G{len(items) + 1:02d}", "scene": p["key"], "loai": kind,
                      "noi_dung": (screen.group(2).strip() if screen else p["noi_dung"][:160]),
                      "goi_y": ", ".join(hints), "file": f"{m['design_id']}-{p['key'].replace(' ', '')}.png", "trang_thai": "Đề xuất"})
    out = Path(m["_dir"]) / "input" / "asset-list.json"
    write_json(out, {"design_id": m["design_id"], "hash_nguon": m["nguon"].get("hash_tong"), "items": items})
    m["asset_list"] = items
    log(m, f"lập Graphic Asset List: {len(items)} đồ hoạ đề xuất")
    save_manifest(m)
    info(f"Graphic Asset List nháp ({len(items)} mục) → {out}")
    for it in items:
        info(f"  {it['id']} · {it['scene']} · {it['loai']} · {it['noi_dung'][:90]}")
    info("Đây là gợi ý máy lọc theo từ khoá — Claude đọc lại script để thêm/bớt, rồi TRÌNH NGƯỜI DÙNG DUYỆT trước khi dựng. "
         "Chỉ dựng đồ hoạ cần thiết.")
    return 0


def sync(args):
    m = manifest(args[0] if args else die(__doc__))
    step = args[1] if len(args) > 1 else die("ia sync <DS> nhan|thieu|xuat-thu")
    tid = m["nguon"].get("task_id") or die("Job không gắn phiếu TASK- nào (việc trực tiếp) — không cần cập nhật 04 Production.")
    note = opt(args, "--note", "")
    if step == "nhan":
        res = run_sheet(["move", tid, "Đang thực hiện"] + (["--note", note] if note else []), check=False)
    elif step == "thieu":
        res = run_sheet(["move", tid, "Thiếu tư liệu", "--note", note or "Agent 02 thiếu tư liệu"], check=False)
    elif step == "xuat-thu":
        link = ((m.get("ban_giao") or {}).get("drive") or {}).get("link")
        if not link:
            die("Chưa có link Drive hợp lệ của thành phẩm (`ia publish` / `ia link`). Không báo đã bàn giao khi chưa có link.", 2)
        r1 = run_sheet(["update", tid, f"Link file hoàn chỉnh={link}"], check=False)
        info(r1.stdout.strip() or r1.stderr.strip())
        res = run_sheet(["move", tid, "Đã xuất file thử", "--note", note or f"{m['design_id']} v{m['ban_duyet']['v']}"], check=False)
    else:
        die("Bước: nhan | thieu | xuat-thu")
    info(res.stdout.strip() or res.stderr.strip())
    if res.returncode == 0:
        log(m, f"cập nhật phiếu {tid}: {step}")
        m["ban_giao"] = m.get("ban_giao") or {}
        m["ban_giao"]["sheet"] = {"buoc": step, "luc": now()}
        if step == "xuat-thu":
            m["trang_thai"] = "Đã bàn giao"
        save_manifest(m)
    return res.returncode


def main(cmd, args):
    if cmd == "content":
        if args and args[0] == "connect":
            return connect(args[1:])
        r = run_sheet(args, check=False)
        print(r.stdout, end="")
        if r.stderr:
            print(r.stderr, end="")
        return r.returncode
    return {"brief": brief, "source-check": source_check, "asset-list": asset_list, "sync": sync}[cmd](args)

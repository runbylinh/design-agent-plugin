"""Học từ số liệu thật: mẫu / bố cục / loại ấn phẩm nào đang thắng.

  ia hieu-qua nhap <file.json|file.csv> --nguon meta|tiktok|organic [--ngay YYYY-MM-DD]
  ia hieu-qua bao-cao [--chi-so ctr|ty_le_luu|ty_le_chia_se|cpr|cpc] [--loai <loại>] [--tu YYYY-MM-DD]
  ia hieu-qua ds <DS>

Mỗi dòng số liệu phải chỉ ra được thiết kế nào: cột chứa mã DS-… (tên quảng cáo, tên file, ghi chú) hoặc Content ID (CT-…) đã gắn job.
Cột số nhận tên Việt hoặc Anh: hien_thi/impressions, tiep_can/reach, click/clicks/link_clicks, luu/saves, chia_se/shares,
binh_luan/comments, chi_phi/spend, ket_qua/results/leads.
Không tự đoán số: dòng không khớp DS nào → liệt kê để người dùng gắn tay.
"""
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

from common import die, find_studio, info, now, read_json, warn, write_json

DS_RX = re.compile(r"DS-\d{6}-\d{2,3}")
CT_RX = re.compile(r"CT-[\w-]+")
ALIAS = {
    "hien_thi": ("hien_thi", "impressions", "luot_hien_thi", "hiển thị", "lượt hiển thị"),
    "tiep_can": ("tiep_can", "reach", "tiếp cận", "lượt tiếp cận"),
    "click": ("click", "clicks", "link_clicks", "inline_link_clicks", "lượt click", "nhấp"),
    "luu": ("luu", "saves", "lưu", "lượt lưu"),
    "chia_se": ("chia_se", "shares", "chia sẻ", "lượt chia sẻ"),
    "binh_luan": ("binh_luan", "comments", "bình luận"),
    "chi_phi": ("chi_phi", "spend", "chi phí", "amount_spent"),
    "ket_qua": ("ket_qua", "results", "leads", "kết quả", "lead"),
}
CHI_SO = {
    "ctr": ("click", "hien_thi", 100, "CTR %", True),
    "ty_le_luu": ("luu", "tiep_can", 100, "lưu / tiếp cận %", True),
    "ty_le_chia_se": ("chia_se", "tiep_can", 100, "chia sẻ / tiếp cận %", True),
    "cpr": ("chi_phi", "ket_qua", 1, "chi phí / kết quả", False),
    "cpc": ("chi_phi", "click", 1, "chi phí / click", False),
}


def _num(v):
    if v in (None, ""):
        return None
    s = str(v).strip().replace("%", "")
    if re.fullmatch(r"[\d.]+,\d+", s):
        s = s.replace(".", "").replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def _rows(path):
    p = Path(path)
    if p.suffix.lower() == ".csv":
        with open(p, encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))
    data = read_json(p)
    if isinstance(data, dict):
        data = data.get("rows") or data.get("data") or data.get("values") or []
    if data and isinstance(data[0], list):
        head = [str(h) for h in data[0]]
        return [dict(zip(head, r)) for r in data[1:]]
    return data


def _jobs(st):
    out = {}
    for f in (st / "jobs").glob("DS-*/manifest.json"):
        m = read_json(f)
        out[m["design_id"]] = m
    return out


def _layouts_of(st, m):
    v = (m.get("ban_duyet") or {}).get("v") or m.get("phien_ban_hien_tai") or 1
    h = (m.get("ban_duyet") or {}).get("huong")
    f = st / "jobs" / m["design_id"] / f"v{v}" / (f"huong-{h}" if h else "") / "design.json"
    if not f.exists():
        return []
    d = read_json(f)
    lays = [p.get("layout") or d.get("layout") for p in d.get("pages", [])] or [d.get("layout")]
    return sorted({x for x in lays if x})


def nhap(args):
    if not args:
        die(__doc__)
    nguon = args[args.index("--nguon") + 1] if "--nguon" in args else die("Thiếu --nguon (meta|tiktok|organic)")
    ngay = args[args.index("--ngay") + 1] if "--ngay" in args else now()[:10]
    st = find_studio()
    jobs = _jobs(st)
    by_ct = defaultdict(list)
    for d, m in jobs.items():
        ct = (m.get("nguon") or {}).get("content_id")
        if ct:
            by_ct[ct].append(d)
    db = read_json(st / "hieu-qua.json", {"ban_ghi": []})
    added, miss = 0, []
    for r in _rows(args[0]):
        low = {str(k).strip().lower(): v for k, v in r.items()}
        blob = " ".join(str(v) for v in r.values())
        ds = sorted(set(DS_RX.findall(blob)))
        if not ds:
            for ct in CT_RX.findall(blob):
                ds += by_ct.get(ct, [])
        ds = [d for d in dict.fromkeys(ds) if d in jobs]
        so = {}
        for key, names in ALIAS.items():
            for nm in names:
                if nm in low and _num(low[nm]) is not None:
                    so[key] = _num(low[nm])
                    break
        if not ds:
            miss.append(blob[:80])
            continue
        if not so:
            warn(f"Dòng của {', '.join(ds)} không có cột số nào nhận ra được — bỏ qua.")
            continue
        for d in ds:
            db["ban_ghi"] = [b for b in db["ban_ghi"] if not (b["ds"] == d and b["nguon"] == nguon and b["ngay"] == ngay)]
            db["ban_ghi"].append({"ds": d, "nguon": nguon, "ngay": ngay, "so": so, "nhap_luc": now()})
            added += 1
    write_json(st / "hieu-qua.json", db)
    info(f"Đã nhập {added} bản ghi ({nguon}, {ngay}) → hieu-qua.json")
    if miss:
        info(f"⚠️ {len(miss)} dòng không khớp thiết kế nào (thiếu mã DS-/CT- đã gắn job) — nhờ người dùng gắn:")
        for x in miss[:10]:
            info(f"   · {x}")
    return 0


def _agg(recs):
    tot = defaultdict(float)
    for r in recs:
        for k, v in r["so"].items():
            tot[k] += v
    return tot


def _val(tot, cs):
    a, b, mul, _, _ = CHI_SO[cs]
    if not tot.get(b):
        return None
    return tot.get(a, 0) / tot[b] * mul


def bao_cao(args):
    cs = args[args.index("--chi-so") + 1] if "--chi-so" in args else "ctr"
    if cs not in CHI_SO:
        die("--chi-so chỉ nhận: " + ", ".join(CHI_SO))
    loai = args[args.index("--loai") + 1] if "--loai" in args else None
    tu = args[args.index("--tu") + 1] if "--tu" in args else ""
    st = find_studio()
    jobs = _jobs(st)
    recs = [r for r in read_json(st / "hieu-qua.json", {"ban_ghi": []})["ban_ghi"] if r["ngay"] >= tu and r["ds"] in jobs]
    if loai:
        recs = [r for r in recs if jobs[r["ds"]].get("loai") == loai]
    if not recs:
        die("Chưa có số liệu (ia hieu-qua nhap …).")
    _, _, _, label, higher = CHI_SO[cs]
    per_ds = defaultdict(list)
    for r in recs:
        per_ds[r["ds"]].append(r)
    ds_val = {d: _val(_agg(rs), cs) for d, rs in per_ds.items()}
    ds_val = {d: v for d, v in ds_val.items() if v is not None}
    if not ds_val:
        die(f"Số liệu chưa đủ cột để tính {label}.")
    groups = {"Mẫu (template)": defaultdict(list), "Bố cục": defaultdict(list), "Loại ấn phẩm": defaultdict(list)}
    for d, v in ds_val.items():
        m = jobs[d]
        goc = m.get("goc") or ""
        if goc.startswith("mau:"):
            groups["Mẫu (template)"][goc[4:]].append(v)
        for lay in _layouts_of(st, m):
            groups["Bố cục"][lay].append(v)
        groups["Loại ấn phẩm"][m.get("loai", "?")].append(v)
    avg = sum(ds_val.values()) / len(ds_val)
    lines = [f"# Hiệu quả thiết kế — {label}" + (f" · {loai}" if loai else ""), "",
             f"{len(ds_val)} thiết kế có số liệu · trung bình {avg:.2f} · {'cao' if higher else 'thấp'} hơn là tốt · cập nhật {now()}", ""]
    for gname, g in groups.items():
        if not g:
            continue
        lines += [f"## {gname}", "| Tên | Số thiết kế | Trung bình | So với chung |", "|---|---|---|---|"]
        rank = sorted(g.items(), key=lambda kv: sum(kv[1]) / len(kv[1]), reverse=higher)
        for name, vals in rank:
            a = sum(vals) / len(vals)
            diff = (a - avg) / avg * 100 if avg else 0
            note = "" if len(vals) >= 3 else " (ít mẫu)"
            lines.append(f"| {name} | {len(vals)}{note} | {a:.2f} | {diff:+.0f}% |")
        lines.append("")
    lines += ["## Từng thiết kế", "| DS | Tên | Loại | Giá trị |", "|---|---|---|---|"]
    for d, v in sorted(ds_val.items(), key=lambda kv: kv[1], reverse=higher):
        lines.append(f"| {d} | {jobs[d].get('ten', '')} | {jobs[d].get('loai', '')} | {v:.2f} |")
    lines += ["", "Ghi chú: nhóm dưới 3 thiết kế chưa đủ kết luận. Chênh lệch còn do nội dung, đối tượng, ngân sách — không chỉ do thiết kế."]
    out = st / "hieu-qua-bao-cao.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    info("\n".join(lines))
    info(f"\n→ {out}")
    return 0


def ds(args):
    st = find_studio()
    d = args[0] if args else die("ia hieu-qua ds <DS>")
    recs = [r for r in read_json(st / "hieu-qua.json", {"ban_ghi": []})["ban_ghi"] if r["ds"] == d]
    if not recs:
        info(f"{d}: chưa có số liệu.")
        return 0
    for r in sorted(recs, key=lambda r: r["ngay"]):
        info(f"{r['ngay']} [{r['nguon']}] " + ", ".join(f"{k}={v:g}" for k, v in r["so"].items()))
    tot = _agg(recs)
    info("Tổng: " + ", ".join(f"{CHI_SO[c][3]}={_val(tot, c):.2f}" for c in CHI_SO if _val(tot, c) is not None))
    return 0


def main(args):
    if not args:
        die(__doc__)
    return {"nhap": nhap, "bao-cao": bao_cao, "ds": ds}.get(args[0], lambda a: die(__doc__))(args[1:])

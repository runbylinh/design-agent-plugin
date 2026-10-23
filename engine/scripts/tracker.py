"""Google Sheet "Hệ thống Design ảnh" — đọc/ghi qua connector Google Sheets của Claude (lệnh này không tự gọi Google).

  ia sheet connect --url <link Sheet> [--media-assets <link thư mục Media Assets>]
  ia sheet init-plan                 in các lệnh tạo cấu trúc (5 tab, tiêu đề dòng 3, dropdown, độ rộng cột) cho Sheet MỚI, trống
  ia sheet pull-plan                 in các vùng cần đọc (get_values) — chạy đầu phiên / khi người dùng vừa sửa Sheet
  ia sheet pull <Tab> --file <kết quả get_values.json>     nạp dữ liệu đọc được vào bộ đệm trên máy
  ia sheet push [--toi-da 12]        in các lệnh ghi (update_values) đang chờ — Claude chạy lần lượt
  ia sheet push --xong <n>           đánh dấu n lệnh đầu đã ghi xong
  ia sheet show <DS-|AS-ID>          một dòng từ bộ đệm
  ia sheet set <DS-|AS-ID> "Cột=giá trị" …   sửa ô (ghi vào hàng đợi)
  ia sheet status                    đã nối chưa, lần đọc gần nhất, số lệnh ghi đang chờ

Tab (khoá): Viec = 01 Brief & Việc · Source = 02 Source · Recap = 03 Recap thiết kế · TieuChuan = 04 Tiêu chuẩn.
Agent chỉ ghi các ô nó thay đổi (không ghi đè cả dòng) để không xoá ghi chú người dùng tự thêm.
Chưa nối Sheet → các bước khác vẫn chạy, chỉ bỏ qua phần ghi Sheet.
"""
import json
import re
import sys
from pathlib import Path

from common import PLUGIN, die, find_studio, info, now, read_json, save_studio_config, studio_config, warn, write_json

SCHEMA = read_json(PLUGIN / "templates" / "tracker.json")
HDR = SCHEMA["header_row"]
TAB_KEYS = list(SCHEMA["tabs"])


def col_letter(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def sheet_id_from_url(url):
    m = re.search(r"/spreadsheets/d/([A-Za-z0-9_-]+)", url or "")
    return m.group(1) if m else (url if re.match(r"^[A-Za-z0-9_-]{30,}$", url or "") else None)


def folder_id_from_url(url):
    m = re.search(r"/folders/([A-Za-z0-9_-]+)", url or "")
    return m.group(1) if m else (url if re.match(r"^[A-Za-z0-9_-]{20,}$", url or "") else None)


# ------------------------------------------------------------------ bộ đệm

def tdir(cfg=None):
    cfg = cfg or studio_config()
    d = Path(cfg["_dir"]) / ".tracker"
    d.mkdir(exist_ok=True)
    return d


def connected(cfg=None):
    cfg = cfg or studio_config()
    return bool((cfg.get("tracker") or {}).get("spreadsheet_id"))


def title(key):
    return SCHEMA["tabs"][key]["title"]


def cache(key, cfg=None):
    return read_json(tdir(cfg) / f"{key}.json", {"headers": [], "rows": [], "pulled": None})


def headers(key, cfg=None):
    c = cache(key, cfg)
    return c["headers"] or SCHEMA["tabs"][key]["columns"]


def outbox(cfg=None):
    return read_json(tdir(cfg) / "outbox.json", {"ops": []})


def save_outbox(ob, cfg=None):
    write_json(tdir(cfg) / "outbox.json", ob)


def find_row(key, id_value, cfg=None):
    idc = SCHEMA["tabs"][key]["id_col"]
    for r in cache(key, cfg)["rows"]:
        if r.get(idc) == id_value:
            return r
    return None


def _next_row(key, cfg):
    c = cache(key, cfg)
    used = [r["_r"] for r in c["rows"]] + [op["row"] for op in outbox(cfg)["ops"] if op["tab"] == key]
    return max(used + [HDR]) + 1


def _queue(key, row, fields, cfg):
    ob = outbox(cfg)
    for op in ob["ops"]:
        if op["tab"] == key and op["row"] == row:
            op["values"].update(fields)
            break
    else:
        ob["ops"].append({"tab": key, "row": row, "values": dict(fields), "luc": now()})
    save_outbox(ob, cfg)
    # cập nhật bộ đệm để lần đọc sau trong cùng phiên thấy ngay
    c = cache(key, cfg)
    for r in c["rows"]:
        if r["_r"] == row:
            r.update(fields)
            break
    else:
        c["rows"].append(dict(fields, _r=row))
    if not c["headers"]:
        c["headers"] = SCHEMA["tabs"][key]["columns"]
    write_json(tdir(cfg) / f"{key}.json", c)


def upsert(key, id_value, fields, cfg=None):
    """Ghi các ô của dòng có ID; chưa có dòng thì thêm dòng mới. Không nối Sheet → bỏ qua."""
    cfg = cfg or studio_config()
    if not connected(cfg):
        return False
    fields = {k: ("" if v is None else v) for k, v in fields.items()}
    idc = SCHEMA["tabs"][key]["id_col"]
    r = find_row(key, id_value, cfg)
    if r is None:
        fields = dict({idc: id_value}, **fields)
        row = _next_row(key, cfg)
    else:
        row = r["_r"]
        fields = {k: v for k, v in fields.items() if str(r.get(k, "")) != str(v)}
        if not fields:
            return True
    _queue(key, row, fields, cfg)
    return True


def append(key, fields, cfg=None):
    cfg = cfg or studio_config()
    if not connected(cfg):
        return False
    _queue(key, _next_row(key, cfg), {k: ("" if v is None else v) for k, v in fields.items()}, cfg)
    return True


def recap(ds, v, buoc, lam="", gop_y="", qa_may="", qa_qa="", quyet_dinh="", ghi_chu="", cfg=None):
    return append("Recap", {"DS ID": ds, "Phiên bản": f"v{v}" if v else "", "Ngày": now(), "Bước": buoc,
                            "Đã làm / đổi gì": lam, "Góp ý người dùng": gop_y, "QA máy": qa_may, "QA design-qa": qa_qa,
                            "Quyết định": quyet_dinh, "Ghi chú": ghi_chu}, cfg)


def hint_push():
    try:
        cfg = studio_config()
    except SystemExit:
        return
    if connected(cfg):
        n = len(outbox(cfg)["ops"])
        if n:
            info(f"📝 Sheet: {n} lệnh ghi đang chờ → `ia sheet push`.")


# ------------------------------------------------------------------ lệnh

def opt(args, name, default=None):
    return args[args.index(name) + 1] if name in args else default


def connect(args):
    cfg = studio_config()
    url = opt(args, "--url") or die("ia sheet connect --url <link Google Sheet>")
    sid = sheet_id_from_url(url) or die("Không đọc được mã Sheet từ link.")
    t = cfg.setdefault("tracker", {})
    t.update({"spreadsheet_id": sid, "url": url.split("?")[0], "schema": SCHEMA["phien_ban"]})
    if opt(args, "--media-assets"):
        fid = folder_id_from_url(opt(args, "--media-assets")) or die("Link Media Assets không hợp lệ.")
        cfg.setdefault("drive", {}).update({"media_assets_id": fid, "media_assets_url": f"https://drive.google.com/drive/folders/{fid}"})
    for k in ("source_id", "final_id", "theo_viec_id", "mau_id"):
        if opt(args, "--" + k.replace("_", "-")):
            cfg.setdefault("drive", {})[k] = folder_id_from_url(opt(args, "--" + k.replace("_", "-")))
    save_studio_config(cfg)
    info(f"Đã nối Sheet {sid}. Tiếp: `ia sheet pull-plan` → đọc → `ia sheet pull …`.")
    return 0


def init_plan(args):
    """Lệnh tạo cấu trúc cho Sheet mới (đang có 1 tab mặc định sheetId 0)."""
    reqs = [{"updateSheetProperties": {"properties": {"sheetId": 0, "title": "00 Hướng dẫn",
                                                       "gridProperties": {"hideGridlines": True}},
                                        "fields": "title,gridProperties.hideGridlines"}},
            {"updateDimensionProperties": {"range": {"sheetId": 0, "dimension": "COLUMNS", "startIndex": 0, "endIndex": 1},
                                           "properties": {"pixelSize": 900}, "fields": "pixelSize"}}]
    purple = {"red": 0.545, "green": 0.361, "blue": 0.965}
    light = {"red": 0.953, "green": 0.933, "blue": 1.0}
    values = [{"range": "'00 Hướng dẫn'!A1", "values": SCHEMA["huong_dan"]}]
    for i, key in enumerate(TAB_KEYS, 1):
        tab = SCHEMA["tabs"][key]
        cols = tab["columns"]
        n = len(cols)
        reqs.append({"addSheet": {"properties": {"sheetId": i, "title": tab["title"], "index": i,
                                                 "gridProperties": {"rowCount": 1000, "columnCount": n, "frozenRowCount": HDR}}}})
        reqs.append({"repeatCell": {"range": {"sheetId": i, "startRowIndex": 0, "endRowIndex": 1, "startColumnIndex": 0, "endColumnIndex": 1},
                                    "cell": {"userEnteredFormat": {"textFormat": {"bold": True, "fontSize": 14}}},
                                    "fields": "userEnteredFormat.textFormat"}})
        reqs.append({"repeatCell": {"range": {"sheetId": i, "startRowIndex": HDR - 1, "endRowIndex": HDR, "startColumnIndex": 0, "endColumnIndex": n},
                                    "cell": {"userEnteredFormat": {"textFormat": {"bold": True, "foregroundColorStyle": {"rgbColor": {"red": 1, "green": 1, "blue": 1}}},
                                                                   "backgroundColorStyle": {"rgbColor": purple}, "wrapStrategy": "WRAP",
                                                                   "verticalAlignment": "MIDDLE"}},
                                    "fields": "userEnteredFormat.textFormat,userEnteredFormat.backgroundColorStyle,userEnteredFormat.wrapStrategy,userEnteredFormat.verticalAlignment"}})
        reqs.append({"repeatCell": {"range": {"sheetId": i, "startRowIndex": HDR, "endRowIndex": 1000, "startColumnIndex": 0, "endColumnIndex": n},
                                    "cell": {"userEnteredFormat": {"wrapStrategy": "WRAP", "verticalAlignment": "TOP"}},
                                    "fields": "userEnteredFormat.wrapStrategy,userEnteredFormat.verticalAlignment"}})
        reqs.append({"repeatCell": {"range": {"sheetId": i, "startRowIndex": HDR, "endRowIndex": 1000, "startColumnIndex": 0, "endColumnIndex": 1},
                                    "cell": {"userEnteredFormat": {"textFormat": {"bold": True}, "backgroundColorStyle": {"rgbColor": light}}},
                                    "fields": "userEnteredFormat.textFormat,userEnteredFormat.backgroundColorStyle"}})
        reqs.append({"updateDimensionProperties": {"range": {"sheetId": i, "dimension": "COLUMNS", "startIndex": 0, "endIndex": n},
                                                   "properties": {"pixelSize": 130}, "fields": "pixelSize"}})
        for c, name in enumerate(cols):
            if name in tab["widths"]:
                reqs.append({"updateDimensionProperties": {"range": {"sheetId": i, "dimension": "COLUMNS", "startIndex": c, "endIndex": c + 1},
                                                           "properties": {"pixelSize": tab["widths"][name]}, "fields": "pixelSize"}})
            if name in tab["enums"]:
                reqs.append({"setDataValidation": {"range": {"sheetId": i, "startRowIndex": HDR, "endRowIndex": 1000, "startColumnIndex": c, "endColumnIndex": c + 1},
                                                   "rule": {"condition": {"type": "ONE_OF_LIST", "values": [{"userEnteredValue": v} for v in tab["enums"][name]]},
                                                            "strict": False, "showCustomUi": True}}})
        last = col_letter(n - 1)
        values.append({"range": f"'{tab['title']}'!A1:{last}{HDR}", "values": [[tab["title"]] + [""] * (n - 1), [tab["mo_ta"]] + [""] * (n - 1), cols]})
        if key == "TieuChuan":
            values.append({"range": f"'{tab['title']}'!A{HDR + 1}", "values": SCHEMA["tieu_chuan"]})
    plan = {"spreadsheet_id": (studio_config().get("tracker") or {}).get("spreadsheet_id", "<id>"),
            "update_spreadsheet": reqs, "update_values": values}
    out = tdir() / "init-plan.json"
    write_json(out, plan)
    info(f"Kế hoạch tạo cấu trúc → {out}")
    info(f"  1 lệnh update_spreadsheet ({len(reqs)} yêu cầu) + {len(values)} lệnh update_values.")
    info("Claude: đọc file đó, chạy update_spreadsheet (requests) rồi lần lượt update_values (range, values). Chỉ dùng cho Sheet MỚI.")
    if "--in" in args:
        print(json.dumps(plan, ensure_ascii=False))
    return 0


def pull_plan(args):
    cfg = studio_config()
    sid = (cfg.get("tracker") or {}).get("spreadsheet_id") or die("Chưa nối Sheet (`ia sheet connect --url …`).")
    info(f"Claude: get_values cho từng vùng (spreadsheetId {sid}), lưu nguyên kết quả JSON ra file rồi `ia sheet pull <Tab> --file …`:")
    for key in TAB_KEYS if not args else args:
        tab = SCHEMA["tabs"][key]
        info(f"  {key:10s} → '{tab['title']}'!A{HDR}:{col_letter(len(tab['columns']) + 4)}")
    ob = outbox(cfg)["ops"]
    if ob:
        warn(f"Còn {len(ob)} lệnh ghi chưa push — push trước khi pull để không mất thay đổi.")
    return 0


def pull(args):
    if not args or args[0] not in TAB_KEYS or "--file" not in args:
        die("ia sheet pull <Viec|Source|Recap|TieuChuan> --file <kết quả get_values.json>")
    key = args[0]
    raw = read_json(opt(args, "--file"))
    vals = raw.get("values", raw) if isinstance(raw, dict) else raw
    if not vals:
        die("File không có dữ liệu (values).")
    hdr = [str(h).strip() for h in vals[0]]
    need = SCHEMA["tabs"][key]["columns"]
    missing = [c for c in need if c not in hdr]
    if missing:
        warn(f"Tab {title(key)} thiếu cột: {', '.join(missing)} — agent sẽ không ghi các cột này. Người dùng đổi tên cột? Báo lại.")
    rows = []
    for i, line in enumerate(vals[1:], HDR + 1):
        if not any(str(x).strip() for x in line):
            continue
        r = {hdr[k]: line[k] for k in range(min(len(hdr), len(line))) if hdr[k]}
        r["_r"] = i
        rows.append(r)
    write_json(tdir() / f"{key}.json", {"headers": hdr, "rows": rows, "pulled": now()})
    info(f"Đã nạp {len(rows)} dòng từ {title(key)}.")
    return 0


def push(args):
    cfg = studio_config()
    sid = (cfg.get("tracker") or {}).get("spreadsheet_id") or die("Chưa nối Sheet.")
    ob = outbox(cfg)
    if "--xong" in args:
        n = int(opt(args, "--xong"))
        ob["ops"] = ob["ops"][n:]
        save_outbox(ob, cfg)
        info(f"Đã đánh dấu {n} lệnh. Còn {len(ob['ops'])}.")
        return 0
    if not ob["ops"]:
        info("Không có gì cần ghi.")
        return 0
    limit = int(opt(args, "--toi-da", 12))
    calls = []
    for op in ob["ops"][:limit]:
        hdr = headers(op["tab"], cfg)
        idx = {h: i for i, h in enumerate(hdr)}
        cells = sorted((idx[k], v) for k, v in op["values"].items() if k in idx)
        skipped = [k for k in op["values"] if k not in idx]
        if skipped:
            warn(f"{title(op['tab'])}: không có cột {', '.join(skipped)} — bỏ qua.")
        # gom các cột liền nhau thành một vùng
        groups, cur = [], []
        for c, v in cells:
            if cur and c != cur[-1][0] + 1:
                groups.append(cur)
                cur = []
            cur.append((c, v))
        if cur:
            groups.append(cur)
        rng = []
        for g in groups:
            a, b = col_letter(g[0][0]), col_letter(g[-1][0])
            rng.append({"range": f"'{title(op['tab'])}'!{a}{op['row']}:{b}{op['row']}", "values": [[v for _, v in g]]})
        calls.append({"op": len(calls) + 1, "update_values": rng})
    plan = {"spreadsheetId": sid, "calls": calls, "con_lai": max(0, len(ob["ops"]) - limit)}
    print(json.dumps(plan, ensure_ascii=False, indent=1))
    info(f"\nClaude: với mỗi phần tử trong calls, chạy update_values cho từng range. Xong → `ia sheet push --xong {len(calls)}`"
         + (f" rồi `ia sheet push` tiếp ({plan['con_lai']} lệnh nữa)." if plan["con_lai"] else "."))
    return 0


def show(args):
    if not args:
        die("ia sheet show <ID>")
    key = "Source" if args[0].startswith("AS-") else "Viec"
    r = find_row(key, args[0])
    if not r:
        die(f"Không thấy {args[0]} trong bộ đệm {title(key)} (pull lại?).")
    print(json.dumps(r, ensure_ascii=False, indent=1))
    return 0


def set_(args):
    if len(args) < 2:
        die('ia sheet set <ID> "Cột=giá trị" …')
    key = "Source" if args[0].startswith("AS-") else "Viec"
    fields = dict(a.split("=", 1) for a in args[1:])
    if not upsert(key, args[0], fields):
        die("Chưa nối Sheet.")
    info(f"Đã xếp hàng ghi {len(fields)} ô cho {args[0]}.")
    hint_push()
    return 0


def status(args):
    cfg = studio_config()
    t = cfg.get("tracker") or {}
    if not t.get("spreadsheet_id"):
        info("Chưa nối Sheet Hệ thống Design ảnh.")
        return 0
    info(f"Sheet: {t.get('url')}")
    for key in TAB_KEYS:
        c = cache(key, cfg)
        info(f"  {title(key):20s} {len(c['rows'])} dòng · đọc lần cuối {c['pulled'] or 'chưa'}")
    info(f"  Lệnh ghi đang chờ: {len(outbox(cfg)['ops'])}")
    d = cfg.get("drive") or {}
    info(f"Media Assets: {d.get('media_assets_url', 'chưa khai báo')}")
    return 0


def recap_cmd(args):
    """ia sheet recap <DS> --buoc Dựng|Sửa|… [--lam "…"] [--gop-y "…"] [--qa-qa "…"] [--quyet-dinh …] — ghi tay (vd. kết quả design-qa)."""
    if not args:
        die('ia sheet recap <DS> --buoc <Bước> [--lam "…"] [--gop-y "…"] [--qa-qa "…"] [--quyet-dinh …] [--v N]')
    ok = recap(args[0], opt(args, "--v", ""), opt(args, "--buoc", "Dựng"), opt(args, "--lam", ""), opt(args, "--gop-y", ""),
               "", opt(args, "--qa-qa", ""), opt(args, "--quyet-dinh", ""), opt(args, "--ghi-chu", ""))
    if not ok:
        die("Chưa nối Sheet.")
    info("Đã xếp hàng một dòng Recap.")
    hint_push()
    return 0


def main(args):
    if not args:
        die(__doc__)
    return {"connect": connect, "init-plan": init_plan, "pull-plan": pull_plan, "pull": pull, "push": push,
            "show": show, "set": set_, "status": status, "recap": recap_cmd}.get(args[0], lambda a: die(__doc__))(args[1:])

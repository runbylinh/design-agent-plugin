---
name: adapt
description: >-
  Tái sử dụng thiết kế của Agent 02 Design — chuyển một thiết kế sang kích thước khác bằng cách dàn lại bố cục (Facebook → Story 9:16, ảnh quảng cáo 4:5, thumbnail, ảnh bìa…), nhân bản hàng loạt từ mẫu đã duyệt cho nhiều chủ đề, tạo biến thể đa kênh, lưu và dùng thư viện mẫu của Brand Kit. Dùng khi người dùng gõ /design-agent:adapt, nói "chuyển sang story / 4:5 / 1:1", "làm thêm các kích thước", "từ mẫu này làm 10 ảnh", "nhân bản cho các chủ đề", "lưu làm mẫu", "dùng mẫu …".
argument-hint: "[DS-ID | tên mẫu]"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/bin/ia:*), Bash(ia:*), Read, Write, Edit, Agent
---

# Đổi kích thước · Nhân bản · Mẫu (D06, D08)

**Lệnh `ia`** = `${CLAUDE_PLUGIN_ROOT}/bin/ia`. Đọc: `references/nguyen-tac.md`, `design-json.md`, `formats/<loại đích>.md`.
Sheet "Hệ thống Design ảnh": pull đầu phiên, `ia sheet push` sau khi xong và trước khi trình duyệt (mỗi bản mới, góp ý, duyệt, bàn giao tự vào tab 01/03) — `references/media-assets.md`.

## Đổi kích thước (D06) — dàn lại, không kéo giãn
1. `ia resize DS --preset <khổ> [--layout <bố cục>]` → job mới, cùng nội dung (chữ khoá giữ mốc cũ), bố cục lấy biến thể đúng tỉ lệ mới.
2. Lệnh báo thành phần đặt tay (`box`) → sửa vị trí cho hợp khổ mới (hoặc chuyển sang `slot`).
3. Đổi khổ thường phải **giảm lượng chữ hiển thị** (story, thumbnail): không cắt chữ đã duyệt — xuống dòng, đổi cỡ; vẫn không vừa → hỏi người dùng
   bỏ dòng phụ nào cho riêng khổ này.
4. `ia render` → mở ảnh: vùng an toàn khổ mới (story: 14% trên / 20% dưới), chủ thể không bị cắt, đọc được trên điện thoại → trình duyệt như skill design.
Nhiều khổ một lúc → mỗi khổ một `ia resize`, trình chung một lượt (ảnh cạnh nhau).

## Nhân bản từ mẫu (D08)
1. Mẫu: một job đã duyệt (DS) hoặc mẫu Brand Kit (`ia template list`). Xem mẫu cho đổi những thành phần nào (`cho_doi`).
2. Viết `rows.json` (một dòng một chủ đề): `[{"ten": "…", "noi_dung": {"<id>": "…"}, "anh": {"<id>": "assets/…"}}]` — chữ lấy từ người dùng/Brief, không tự viết.
3. `ia batch <DS|mẫu> --data rows.json` → các job mới → `ia render` từng job → mở `xem-dien-thoai.png` từng ảnh: chữ dài/ngắn khác nhau có làm vỡ bố cục?
   Ảnh nào phải thu nhỏ chữ nhiều → chỉnh riêng ảnh đó (xuống dòng/cỡ), báo người dùng.
4. Trình theo lô (ghép ảnh xem nhanh hoặc liệt kê đường dẫn) → duyệt từng ảnh hoặc cả lô (ghi rõ trong `--xac-nhan`).
Lô ≥ 6 job → có thể giao subagent dựng + tự kiểm theo nhóm; approve/export do bộ điều phối.

## Thư viện mẫu
- Lưu: `ia template save DS --ten <tên-không-dấu> --cho-doi <id1,id2> --mo-ta "…"` (chỉ bản đã duyệt). Hỏi người dùng phần nào được đổi khi dùng lại.
- Dùng: `ia template use <tên> --ten "…" [--ct CT-…]` → sửa nội dung các thành phần được đổi. Mẫu là điểm xuất phát: được biến đổi trong tinh thần chung,
  không ép mọi thiết kế giống hệt.

Sau duyệt: export → publish → link → sync như skill design mục 6.

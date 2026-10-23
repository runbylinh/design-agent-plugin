---
name: status
description: >-
  Xem nhanh tình hình Agent 02 Ảnh — job thiết kế đang làm, chờ duyệt, chờ upload Drive, đã bàn giao; mở lại việc cũ theo DS ID, Content ID, Task ID hoặc tên ("bộ ảnh của video hôm qua"); xem lịch sử phiên bản, bản đã duyệt, link Drive; phát hiện Brief/Script nguồn đã đổi; tiếp tục việc dở sau gián đoạn. Dùng khi người dùng gõ /image-agent:status, hỏi "agent ảnh đang tới đâu", "còn ảnh nào chờ duyệt", "mở lại ảnh …", "file ảnh CT-… ở đâu", "những file chưa duyệt của video hôm qua", "upload xong chưa".
argument-hint: "[DS-ID | CT-ID | từ khoá]"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/bin/ia:*), Bash(ia:*), Read
---

# Tình hình & mở lại việc cũ

**Lệnh `ia`** = `${CLAUDE_PLUGIN_ROOT}/bin/ia`, chạy trong studio.

## Tổng quan
Sheet đã nối → `ia sheet pull-plan` + pull trước (người dùng có thể đã sửa trạng thái/ghi chú trên Sheet), `ia sheet status` (còn lệnh ghi chờ → push). Gửi kèm link Sheet để người dùng xem tab 01/03.
`ia status` (thêm `--cho-duyet`, `--dang-lam`, `--cho-upload`, `--tat-ca`). Trình ngắn: số việc theo nhóm, việc cần người dùng (chờ duyệt, chờ kéo file lên Drive),
việc quá hạn (đối chiếu hạn trong `input/brief.json`).
Job từ Agent Content còn dở → `ia source-check DS` từng job (mã thoát 3 = nguồn đổi → báo, gợi ý skill edit).

## Mở lại việc cũ
`ia job find <từ khoá | DS | CT | TASK>` → `ia job show DS`: trình bản đã duyệt (v, lúc, lời duyệt), bản đang sửa, link Drive, trạng thái bàn giao, nhật ký gần nhất.
"Ảnh của video hôm qua" → `ia status --tat-ca` lọc theo `cap_nhat`/tên, đưa lựa chọn nếu nhiều.
Cho người dùng xem ảnh: đường dẫn `jobs/DS/approved/` (bản duyệt) hoặc `jobs/DS/vN/out/` (bản đang làm).

## Tiếp tục việc dở
| Trạng thái | Làm tiếp |
|---|---|
| Mới / Đang làm | mở design.json phiên bản hiện tại → `ia render` → tiếp skill design mục 4 |
| Chờ duyệt | trình lại ảnh phiên bản hiện tại, chờ người dùng |
| Đã duyệt (chưa xuất) | `ia export` |
| Chờ upload | `ia publish` đã chạy → kiểm Drive bằng connector (`search_files parentId`) → `ia link … --kiem` |
| Đã duyệt + có link, chưa sync | `ia sync DS xuat-thu` |
Lỗi dựng (Chromium/font) → `ia doctor`; design.json vẫn còn nên không phải làm lại từ đầu.

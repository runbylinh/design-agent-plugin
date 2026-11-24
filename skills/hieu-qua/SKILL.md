---
name: hieu-qua
description: >-
  Học từ số liệu thật để biết mẫu thiết kế, bố cục, loại ấn phẩm nào đang thắng — lấy số quảng cáo (Meta Ads qua connector, TikTok Ads từ file), số organic (tab 06 Performance của Agent Content, file người dùng xuất), gắn vào từng thiết kế theo mã DS / Content ID, xếp hạng theo CTR, tỉ lệ lưu, tỉ lệ chia sẻ, chi phí/kết quả, viết báo cáo và đề xuất mẫu nên dùng tiếp / nên bỏ / nên thử biến thể. Dùng khi người dùng gõ /design-agent:hieu-qua, hỏi "mẫu nào hiệu quả nhất", "thiết kế nào CTR cao", "carousel kiểu nào được lưu nhiều", "ảnh quảng cáo nào thắng", "học từ số liệu ads", "nên dùng template nào tiếp".
argument-hint: "[chỉ số | loại ấn phẩm | khoảng thời gian]"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/bin/ia:*), Bash(ia:*), Read, Write, Edit
---

# Học từ số liệu hiệu quả

**Lệnh `ia`** = `${CLAUDE_PLUGIN_ROOT}/bin/ia`, chạy trong studio. Không tự đoán số, không bịa chỉ số. Tiếng Việt, lời thường.

## 1. Chốt câu hỏi
Ấn phẩm nào (quảng cáo / carousel / thumbnail…), khoảng thời gian, chỉ số theo mục tiêu:
quảng cáo kéo click → `ctr`, `cpc` · quảng cáo lead/đơn → `cpr` · bài organic kiến thức → `ty_le_luu`, `ty_le_chia_se`.

## 2. Lấy số liệu (ghi ra file JSON/CSV trong `nhap/` của studio rồi `ia hieu-qua nhap`)
- **Meta Ads (connector):** tài khoản quảng cáo (`ads_get_ad_accounts` nếu chưa biết) → `ads_get_ad_entities` cấp quảng cáo, kèm số hiển thị, tiếp cận,
  click, chi phí, kết quả trong khoảng thời gian → ghi mỗi quảng cáo một dòng `{ "ten": <tên quảng cáo>, "impressions": …, … }`.
  Quảng cáo phải có **mã DS trong tên** (quy ước ở `formats/quang-cao.md`); không có → hỏi người dùng quảng cáo nào dùng thiết kế nào.
- **TikTok Ads / số organic xuất file:** người dùng để file CSV vào `nhap/` → nhập thẳng (cột có DS-/CT-).
- **Organic từ Agent Content:** đọc tab `06 Performance` (connector Google Sheets `get_values`) → mỗi dòng có Content ID (CT-…) → ghi JSON → nhập;
  máy tự nối CT- với job DS đã gắn Content ID.
`ia hieu-qua nhap <file> --nguon meta|tiktok|organic [--ngay <ngày chốt số>]` → dòng không khớp được thiết kế nào thì đưa danh sách cho người dùng gắn.

## 3. Báo cáo
`ia hieu-qua bao-cao --chi-so <…> [--loai …] [--tu …]` → đọc `hieu-qua-bao-cao.md`. Mở ảnh (`jobs/DS/approved/`) của 3 thiết kế cao nhất và 3 thấp nhất,
so bằng mắt: khác nhau ở bố cục, ảnh người, màu nền, độ dài tiêu đề, CTA?
Trình ngắn: xếp hạng mẫu/bố cục (bỏ qua nhóm "ít mẫu" khi kết luận), 2–3 điểm chung của nhóm thắng (kèm DS minh hoạ), đề xuất:
**dùng tiếp** (mẫu nào, cho việc gì) · **dừng** · **thử biến thể** (đổi đúng một yếu tố — `formats/quang-cao.md`).
Luôn nhắc: chênh lệch còn do nội dung, đối tượng, ngân sách; dưới 3 thiết kế một nhóm thì chưa kết luận.

## 4. Áp dụng (khi người dùng đồng ý)
- Ghi kết luận vào `brand.md` mục "Style đã học" (học từ số liệu, khoảng thời gian, chỉ số) — skill design đọc mục này trước khi chọn mẫu.
- Mẫu thắng → ưu tiên trong `ia template list` (đổi `--mo-ta` khi lưu lại, thêm "✓ hiệu quả <chỉ số>"); mẫu thua → đề xuất xoá hoặc làm lại qua skill research.
- Có giả thuyết mới → tạo bộ biến thể bằng `ia batch` / skill design (D10) để thử vòng sau.

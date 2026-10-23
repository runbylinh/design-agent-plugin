# Điều phối — nhận diện yêu cầu, chuẩn hoá Brief, 15 Use Case

## 1. Input Router (chạy ngầm, không bắt người dùng chọn)
| Dấu hiệu | Đầu vào | Nhánh |
|---|---|---|
| Có `TASK-…` / `CT-…`, "phiếu", "Brief của Agent Content", "trong Production" | B1 Brief ảnh từ Agent 01 | thiết kế mới (D01/D13) |
| Có script/kịch bản video, "đồ hoạ cho video", `[Cảnh n]`, `SC-…` | B2 Script video | Graphic Asset List (D14) |
| Agent Video / người dùng nêu đồ hoạ cụ thể cho video | Video Graphic Brief | thiết kế mới (D12) |
| Đưa ảnh/file thiết kế cũ + "sửa", "giữ nguyên…, chỉ đổi…" | A — sửa | `edit` (D05) |
| "Chuyển sang story/4:5/…", "làm thêm kích thước" | A — đổi khổ | `adapt` (D06) |
| "Từ mẫu này làm 10 ảnh…", danh sách chủ đề | A — nhân bản | `adapt` (D08) |
| "Làm giống bố cục ảnh này" + ảnh tham khảo | A — theo tham khảo | thiết kế mới (D07) |
| "Bộ ảnh cho chiến dịch…" nhiều vai trò | A — bộ chiến dịch | thiết kế mới (D09) |
| Còn lại: mô tả + chữ (+ ảnh) | A — trực tiếp | thiết kế mới (D02/D03/D04…) |
| "Bài tuần này", "ảnh của video hôm qua" | mơ hồ | tìm trong Production (`ia content get Production …`) và job cũ (`ia status`, `ia job find`) → đưa lựa chọn |

Chỉ đọc Content Workspace khi yêu cầu liên quan Content ID / Campaign / Script / phiếu Production. Việc độc lập không cần.

## 2. Design Brief chuẩn hoá (ghi vào `jobs/DS/input/design-brief.md`)
```
DESIGN BRIEF — DS-… (nguồn: trực tiếp | TASK-… / CT-… bản V2 | script SC-01…SC-08)
Mục tiêu: …                         Loại ấn phẩm / khổ: … (preset)
Nội dung (đã duyệt / người dùng đưa — KHOÁ): …
Thứ tự ưu tiên thông tin: 1… 2… 3…
Tư liệu dùng: AS-… / file người dùng / tách nền …   Còn thiếu: …
Thành phần giữ nguyên (style_locked): …
Số phương án: 1 | 2–3 (lý do)       Hạn: …
Không được: …
```
Hỏi người dùng **chỉ những gì thật sự thiếu**, gom vào một lượt. Phát sinh vấn đề sau đó (ảnh không đủ chất lượng, quyền dùng ảnh,
nội dung quá dài, nguồn đổi) → được hỏi thêm trước khi làm sai.
Việc nhỏ (đổi logo, thay chữ, đổi màu nền) → làm luôn, không trình Design Brief.

## 3. Số phương án
| Tình huống | Số bản |
|---|---|
| Thiết kế mới, chưa có mẫu, Brief chưa rõ hướng | 2–3 hướng (`huong-a/b/c`) khác nhau thật (bố cục / cách thể hiện), không chỉ đổi màu |
| Có mẫu đã duyệt hoặc Brief ghi rõ bố cục | 1 bản chính |
| Chỉnh sửa | chỉ phần được yêu cầu |
| Biến thể quảng cáo (D10) | đúng số biến thể Brief yêu cầu |

## 4. 15 Use Case → skill
| Mã | Use Case | Skill | Ghi chú |
|---|---|---|---|
| D01 | Thiết kế từ Brief Agent Content | design | = D13 khi Brief đã duyệt |
| D02 | Chỉ từ nội dung chữ | design | formats/facebook.md §D02 |
| D03 | Carousel nhiều trang từ bài dài | design | formats/carousel.md — không tự cắt nội dung |
| D04 | Ấn phẩm hoạt động (poster, mở bán, lịch học) | design | formats/poster.md |
| D05 | Sửa thiết kế có sẵn | edit | có design.json / chỉ có PNG |
| D06 | Chuyển nhiều kích thước | adapt | `ia resize` — dàn lại, không kéo giãn |
| D07 | Theo ảnh tham khảo | design | chỉ học cấu trúc bố cục |
| D08 | Hàng loạt từ mẫu | adapt | `ia batch` |
| D09 | Bộ ấn phẩm chiến dịch | design | nhiều job, một hệ thống |
| D10 | Biến thể quảng cáo | design | formats/quang-cao.md |
| D11 | Số liệu, case study | design | formats/bieu-do.md |
| D12 | Đồ hoạ cho Agent Video (yêu cầu cụ thể) | design | formats/video-graphic.md |
| D13 | Brief ảnh đã duyệt từ Agent 01 | design | hop-dong-ban-giao.md |
| D14 | Script video → Graphic Asset List | design | duyệt danh sách trước khi dựng |
| D15 | Nguồn đổi sau khi đã bắt đầu | status / edit | `ia source-check` |

## 5. Bộ chiến dịch (D09)
Một chiến dịch = nhiều job (mỗi vai trò một job: thu hút, giới thiệu, lợi ích, ưu đãi, nhắc hạn…), cùng `--ct`/tên chiến dịch trong `--ten`.
Làm job đầu tiên (ảnh chủ đạo) → duyệt → `ia template save` làm mẫu chiến dịch → các job sau `ia template use` để thống nhất hệ thống,
nhưng mỗi vai trò có bố cục phù hợp (không bắt mọi ảnh giống hệt).

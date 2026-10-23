# Hợp đồng bàn giao Content → Ảnh → Video — contract v1

> Bản gốc dự kiến đặt ở content-agent (nơi phát Brief). Bản này là bản sao Agent 02 đang theo: **contract v1**.
> Lệch phiên bản → báo người dùng, không tự đoán trường mới.

## 1. Agent 01 → Agent 02 (phiếu `04 Production`, Agent phụ trách = "Agent 02 – Ảnh")
| Cột 04 Production | Agent 02 dùng làm |
|---|---|
| Task ID | `--task` của job, khoá nguồn |
| Content ID / Parent Content ID | `--ct` |
| Loại nhiệm vụ (Ảnh đơn / Carousel / Thumbnail / Resize ảnh) | `--loai` (Ảnh đơn→facebook, Carousel→carousel, Thumbnail→thumbnail, Resize ảnh→`ia resize`) |
| Kênh · Format · Kích thước / tỷ lệ | preset |
| Hook / Caption / Kịch bản | **chữ đã duyệt** → `content_locked` (tách theo `Trang n` / `[Cảnh n]` / `SC-xx`) |
| Brief ảnh / video | Design Brief (mẫu `content-agent/references/viet/brief-anh.md`) |
| Link tư liệu / Brand Kit | tư liệu (ảnh thật, logo) |
| Trạng thái duyệt chữ | phải = Đã duyệt mới sản xuất chính thức |
| Phiên bản (tuỳ chọn) | `ban_nguon` |
| Hạn hoàn thành | hạn job |

Script video: mỗi cảnh **nên có Scene ID cố định** `SC-01…` (không đổi khi chèn/xoá cảnh). Chưa có → Agent 02 dùng "Cảnh n" và cảnh báo.

## 2. Agent 02 → Agent 01 (ghi qua `sheet` của content-agent)
| Bước | Lệnh | Cột / trạng thái |
|---|---|---|
| Nhận việc | `ia sync DS nhan` | Trạng thái sản xuất → Đang thực hiện |
| Thiếu tư liệu | `ia sync DS thieu --note "…"` | → Thiếu tư liệu |
| Có thành phẩm trên Drive | `ia sync DS xuat-thu` | Link file hoàn chỉnh = link thư mục Drive; → Đã xuất file thử |

Một carousel / một Graphic Pack = **một link thư mục**, không mười cột. DS ID nằm trong tên thư mục và ghi chú chuyển trạng thái.
Agent 02 không ghi Kết quả QA / Đạt QA / Hoàn thành / Duyệt 04.

## 3. Nội dung có vấn đề
Quá dài cho khổ, thiếu thông tin bắt buộc, mâu thuẫn Brand Kit → **không tự sửa chữ**: `ia sync DS thieu --note "<vấn đề + đề xuất>"`,
báo người dùng để Agent 01 sửa (`sheet move CT-… "Cần sửa chữ"` là việc của Agent 01).

## 4. Khoá nguồn & thay đổi (D15)
`ia brief` lưu mã băm toàn bộ + từng trang/cảnh. Trước khi bàn giao và khi mở lại job: `ia source-check DS`.
Đổi → liệt kê phần sửa/thêm/bỏ + đồ hoạ bị ảnh hưởng → đề xuất giữ/sửa/thêm/bỏ → bản mới chờ duyệt. Không tự thay file đã bàn giao.

## 5. Agent 02 → Agent 03 Video (Graphic Pack)
Thư mục Drive `Media Assets/01 Ảnh/02 Final/<YYYY-MM>/<DS-… · tên>/`: `DS-…-SC-xx.png` (trong suốt) + `_nguon/` (`huong-dan-dat.md`, `design.json`, `manifest.json`).
Agent Video nhận link thư mục (hoặc đường dẫn `approved/` nếu cùng máy).

## 6. Sheet "Hệ thống Design ảnh" của Agent 02
Mỗi phiếu TASK nhận về có một dòng DS ở tab 01 Brief & Việc (cột TASK ID, CT ID). Brief chép sang **chỉ đọc**.
Link Final ghi vào cả tab 01 (Sheet ảnh) và cột Link file hoàn chỉnh (04 Production).

## 7. Mã
- Job: `DS-YYMMDD-NN` (Agent 02 tự cấp, kể cả việc trực tiếp không có Content ID).
- Tài nguyên: `AS-NNN`.

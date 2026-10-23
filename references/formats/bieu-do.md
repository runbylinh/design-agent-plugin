# Đồ hoạ dữ liệu — biểu đồ, bảng, case study (D11)

**Nguyên tắc số 1: không đặt ra số.** Mọi con số đến từ người dùng, Brief đã duyệt, file dữ liệu / ảnh chụp màn hình người dùng đưa. Không có → hỏi.

## Chọn kiểu
| Muốn nói | Kiểu (`spec.kind`) |
|---|---|
| So sánh vài nhóm | `bar` (nhãn dài → `hbar`) |
| Xu hướng theo thời gian | `line` |
| Tỉ trọng 2–5 phần | `donut` (không quá 5 phần) |
| Các bước rơi rụng | `funnel` |
| Trước / sau, nhiều tiêu chí | `compare` / `table` |
| Một con số nổi bật | text `role: stat` cỡ `mega` + 1 dòng giải thích (bố cục `so-lieu`) |

## Bắt buộc
- `unit` (đơn vị) đúng; nhãn trục / nhãn cột rõ; số làm tròn hợp lý (giữ nguyên số người dùng đưa nếu đã làm tròn).
- `source`: nguồn + khoảng thời gian (vd. "Meta Ads Manager, 01–31/10/2026"). Thiếu → QA chặn.
- `highlight`: một điểm cần người xem chú ý (cột / điểm cuối).
- Trục cột bắt đầu từ 0 (engine vẽ vậy) — không cắt trục để phóng đại.
- Ảnh chụp màn hình số liệu (D11): đọc số → dựng lại thành biểu đồ sạch; che thông tin cá nhân/tài khoản nếu dùng ảnh chụp gốc.

## Tiêu đề biểu đồ
Viết dạng kết luận ("CPA giảm 47% sau khi gộp nhóm") **chỉ khi** kết luận đó có trong Brief/người dùng nói; không thì dùng tiêu đề mô tả ("Chi phí / đơn theo tuần").

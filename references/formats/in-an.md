# Ấn phẩm in (`ia job new --loai in_an`)

| Khổ (preset) | Kích thước thật | Tràn lề | dpi | Dùng cho |
|---|---|---|---|---|
| `in_namecard` | 90×54mm | 3mm | 300 | danh thiếp |
| `in_a4_doc` | 210×297mm | 3mm | 300 | tờ rơi, poster nhỏ, tài liệu phát tay |
| `in_a4_ngang` | 297×210mm | 3mm | 300 | chứng nhận, giấy mời |
| `in_a3_doc` | 297×420mm | 3mm | 200 | poster dán tường |
| `in_standee` | 60×160cm | 5mm | 100 | standee chân chữ X |
| `in_banner_cuon` | 80×200cm | 5mm | 72 | banner cuốn (roll-up) |
| `in_backdrop` | 3×2m | 10mm | 50 | backdrop sân khấu, phông chụp ảnh |
Khổ khác → `canvas: {"w": …, "h": …}` tính theo công thức `(mm + 2×tràn lề) / 25,4 × dpi`, và hỏi xưởng in thông số trước.

## Quy tắc
- **Nền, ảnh tràn, khối màu sát mép phải phủ hết vùng tràn lề** (kéo ra tới mép file). Phần tràn lề bị xén mất khi cắt.
- **Chữ, logo, số điện thoại, QR** nằm trong vùng an toàn (máy báo lỗi nếu đè vùng tràn lề, cảnh báo nếu ra ngoài vùng an toàn).
- Ảnh: độ phân giải thật đủ cho khổ in (`ia inspect` — ảnh nhỏ hơn ~70% kích thước cần → báo người dùng). Logo dùng bản gốc chất lượng cao (SVG/PNG lớn).
- Khổ lớn (standee, banner, backdrop) đọc từ xa: tiêu đề chiếm ~1/5 chiều cao vùng nội dung, tối đa ~25 từ cả ấn phẩm, thông tin chính ở 2/3 trên (standee/banner phần dưới hay bị che).
- Chữ thân ≥ 8pt khi in A4 (≈ 33px ở 300dpi); danh thiếp ≥ 7pt.
- QR: cạnh ≥ 2cm, nền trắng quanh mã, kiểm quét được trước khi gửi in.

## Xuất
`ia export DS` → PNG + PDF đúng kích thước thật (đã gồm tràn lề). `--cmyk` → thêm `DS-cmyk.pdf` chuyển màu CMYK đơn giản (màu sáng/neon như hồng, cyan có thể xỉn —
báo người dùng xem bản in thử). Nhiều xưởng nhận PDF RGB; hỏi xưởng trước khi chọn.
Lời bàn giao luôn ghi: kích thước thật, tràn lề bao nhiêu mm mỗi cạnh, dpi, "xén theo kích thước thật", màu RGB hay CMYK.

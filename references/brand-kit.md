# Brand Kit — thiết lập & dùng

Brand Kit là **thư mục** (dùng chung với plugin video-edit — cùng `brand.json`):
```
brand-kit/<brand>/
  brand.json      màu, font, logo, image (bo góc, lề, phong cách), rules (nên/không)   ← máy đọc
  brand.md        tinh thần thương hiệu, cách dùng màu/chữ/logo/ảnh — bằng lời          ← Claude đọc trước mọi thiết kế
  logo/           logo các phiên bản (nền sáng, nền tối, biểu tượng)
  fonts/          file font thương mại (font Google tải bằng `ia font get`)
  anh-mau/        5–10 ảnh "đúng chất" đã duyệt — nguồn chính để nắm tinh thần
  mau/            mẫu thiết kế đã duyệt (`ia template save`) — design.json + ảnh xem trước
  thanh-phan/     thành phần dùng lại (khung chữ, nền, nút, hoạ tiết); bố cục riêng của brand: thanh-phan/layouts/<tên>.json
```
Nếu brand đã có Brand Kit bên video-edit (`video-studio/brand-kit/<brand>`): nối luôn (`ia studio init … --brand-kit <thư mục>` hoặc `ia brand init <brand> --tu <thư mục>`).
Agent 02 chỉ **thêm** khối `fonts`, `logos`, `image`, `rules` vào brand.json; không đụng `captions`, `zoom`, `music`, `color_grade` của video-edit.

## Đọc guideline → Brand Kit (setup)
Đầu vào: PDF / link / ảnh guideline + ảnh mẫu đã duyệt.
1. Đọc kỹ guideline (PDF: đọc từng trang; ảnh: xem). Lấy màu từ logo/ảnh: `ia brand colors <ảnh…>`.
2. Ghi brand.json:
   - `colors`: primary, secondary, highlight (màu nhấn), dark (chữ trên nền sáng), light (nền nhạt), paper (nền), + màu phụ có tên (pink…).
     Kiểm màu nhấn có đủ tương phản trên nền sáng **và** nền tối không; không đủ → ghi 2 màu (vd. `highlight` cho nền tối, `pink` cho nền sáng) và ghi rõ trong brand.md.
   - `fonts.heading/body` (family, weight). Font Google → `ia font get`. Font thương mại → xin file, chép vào fonts/.
   - `logos`: [{file, variant, nen: sang|toi}] — cần ít nhất bản nền sáng + bản nền tối.
   - `image`: radius, spacing, style (1 câu), photo_style.
   - `rules.nen_lam` / `rules.khong_lam`: quy tắc cụ thể kiểm được (không chung chung).
3. Viết brand.md theo `templates/brand-kit/brand.md` — mục **[CẦN XÁC NHẬN]** cho điều suy ra.
4. Ảnh mẫu → `anh-mau/` + một dòng "vì sao đúng chất" trong brand.md.
5. `ia brand check` → sửa đến khi ✅.
6. **Dựng thử 2–3 mẫu** (vd. 1 thumbnail, 1 trang carousel, 1 ảnh FB chỉ chữ) với nội dung thật của brand → người dùng duyệt / góp ý.
   Góp ý thành quy tắc → thêm vào `rules` + brand.md. Bản duyệt → `ia template save` làm mẫu đầu tiên.

## Dùng khi thiết kế
- Luôn đọc brand.md + `ia brand show` + xem `anh-mau/` và `mau/` liên quan trước khi dựng.
- Mẫu đã duyệt là điểm xuất phát, không phải khuôn cứng: được đổi bố cục/biến thể trong tinh thần chung; không ép mọi ảnh giống hệt.
- Mỗi góp ý lặp lại của người dùng ("logo to quá", "đừng dùng nền tím đậm") → thêm vào `rules.khong_lam` để lần sau không lặp.

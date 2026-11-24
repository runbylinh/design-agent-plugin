# Slide / deck (`slide_16x9` 1920×1080)

**Việc của deck:** người nghe theo kịp một mạch, mỗi slide một ý nhìn là hiểu; người xem lại file vẫn hiểu không cần người nói.

## 1. Trục và dàn slide
- **Trục câu chuyện** = 1 câu: người nghe đi từ đâu đến đâu (vd "từ đăng bài theo cảm hứng → có kế hoạch content đo được").
- Cấu trúc thường dùng: Bìa → (Mục lục) → mỗi chương: slide chương + 2–6 slide nội dung → Tổng kết → Kết/CTA.
- Đào tạo: ~1 slide / 1–2 phút nói. Deck 20 slide trở lên phải có slide chương và số chương để không lạc.
- Mỗi slide một ý: tiêu đề slide là **câu kết luận** của slide (đọc lướt chỉ tiêu đề vẫn hiểu mạch), không phải nhãn chung ("Nội dung", "Phần 2").

| Loại | Bố cục | Ghi chú |
|---|---|---|
| Bìa | `slide-bia` | tên bài ≤ 10 từ, nhãn buổi/ngày, người trình bày, logo |
| Chương | `slide-chuong` | số chương lớn + tên chương, gần như không có chữ khác |
| Nội dung | `slide-noi-dung` / `slide-noi-dung-anh` | tiêu đề + 3–5 ý ≤ 12 từ/ý; có ảnh/sơ đồ thì dùng bản `-anh` |
| So sánh | `slide-hai-cot` | trước/sau, nên/không nên, hai lựa chọn — vùng `cot1`, `cot2` (`"slot": "cot1"`) |
| Số liệu | `so-lieu` | 1–3 con số lớn có nguồn |
| Trích dẫn / thông điệp | `tieu-de-giua` | một câu |
| Kết | `slide-ket` | câu chốt + CTA/liên hệ |

## 2. Chữ
- Tiêu đề slide ≤ 10–12 từ; thân ≤ 40 từ/slide. Chữ nhỏ nhất ≥ 24px (ở 1920px). Không viết hoa toàn bộ tiêu đề.
- Nhiều chữ hơn → tách slide hoặc chuyển phần giải thích vào ghi chú người nói (ghi trong design-brief), **không tự cắt nội dung đã chốt**.

## 3. Hình
- Nền theo brand.md (deck đào tạo thường nền sáng, nhiều khoảng trắng). Mỗi slide tối đa một điểm nhấn màu.
- Ảnh chụp màn hình phần mềm: chiếm phần lớn vùng ảnh; cần chỉ chỗ nào → `shape` mũi tên/khung mảnh.
- Sơ đồ quy trình: `shape` + `text` có `box`, hoặc `chart` kiểu bảng/phễu. Không dùng minh hoạ AI có chữ.

## 4. Kiểm cả bộ (`xem-nhanh.png`)
- Cùng hệ lưới: tiêu đề cùng vị trí, lề đều, logo/số trang cùng chỗ ở slide nội dung.
- Đọc lần lượt các tiêu đề → ra đúng trục câu chuyện.
- Không slide nào nhồi chữ hoặc trống trơn ngoài slide chương; không quá 3 cỡ chữ một slide.
- Chính tả, dấu tiếng Việt; số liệu đúng nguồn.

## 5. Xuất sang Canva
- `ia export DS --dinh-dang png,pdf,pptx`. PPTX: mỗi slide = ảnh nền (khối màu, ảnh, logo) + hộp chữ thật sửa được.
- Canva: Tải lên (Uploads) → chọn `.pptx` → Canva tạo thiết kế. Font: Canva chỉ nhận thường/đậm; nếu chữ hiện sai font → chọn một khối chữ → đổi font → "Thay đổi tất cả".
- Chữ tô gradient không giữ được trong PPTX → thành màu đen, chỉnh lại trên Canva (ghi vào lời bàn giao).
- PDF nhập vào Canva hay lệch font → luôn dùng PPTX.

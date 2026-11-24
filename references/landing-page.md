# Landing page — cấu trúc, chữ, HTML, kiểm tra

Một trang = một mục tiêu = một hành động chính. Người xem đọc lướt trên điện thoại: màn đầu phải nói được "đây là gì, cho ai, được gì, bấm đâu".

## 1. Brief tối thiểu
| Mục | Vì sao cần | Thiếu thì |
|---|---|---|
| Mục tiêu + hành động chính | quyết định cấu trúc và nút | hỏi |
| Khách xem là ai, đang gặp vấn đề gì | viết hero + section vấn đề | suy từ nội dung, ghi [CẦN XÁC NHẬN] |
| Lời hứa chính | H1 | hỏi |
| Offer / giá / hạn / quà | khối Offer | không có → bỏ khối, **không bịa** |
| Bằng chứng có thật (số liệu, feedback, logo, ảnh) | tăng tin | không có → bỏ khối |
| Đích của nút (link form, Zalo, hotline, #form) | CTA hoạt động | hỏi; tạm `#dang-ky` và báo rõ |
| Ảnh có sẵn | hero, người dẫn, sản phẩm | dùng chữ + khối màu, báo cảnh thiếu |

## 2. Khung theo mục tiêu (chọn và bỏ bớt, không bắt buộc đủ)
| Mục tiêu | Thứ tự section gợi ý |
|---|---|
| `dang-ky` (lead, tài liệu, buổi tư vấn) | Hero (nhãn · H1 · 1 câu · nút) → Vấn đề (3 thẻ) → Nhận được gì (3–4 thẻ) → Người dẫn/Đơn vị (ảnh + 3 số) → Form/CTA → FAQ 4 câu → Chân trang |
| `ban-hang` (khoá học, sản phẩm) | Hero → Dành cho ai / vấn đề → Giải pháp & kết quả → Nội dung chương trình/tính năng (accordion hoặc thẻ) → Bằng chứng (số, feedback) → Người dạy/Đơn vị → Offer + giá + hạn → Cam kết → FAQ → CTA cuối |
| `su-kien` (workshop, webinar) | Hero (tên, ngày giờ, hình thức, nút) → Học/được gì (3–4 ý) → Lịch trình → Diễn giả → Dành cho ai → Đăng ký (đếm chỗ/hạn nếu có thật) → FAQ |
| `gioi-thieu` (dịch vụ, thương hiệu) | Hero → Dịch vụ (thẻ) → Quy trình (3–5 bước số) → Kết quả/case → Đội ngũ → Liên hệ |
CTA chính lặp lại ở hero, giữa trang và cuối trang (cùng chữ, cùng đích).

## 3. Viết chữ
- **Ít chữ**: gộp khối trùng ý; mỗi thẻ = tiêu đề + 1 dòng (~8–12 chữ, đủ nghĩa, đừng cắt cụt). Hero: nhãn + H1 (≤ 14 chữ) + 1 câu + nút.
- Nói bằng kết quả cụ thể (thời gian, chi phí, việc làm được), không tính từ chung chung. Giọng chuyên nghiệp, câu trần thuật rõ; FAQ hỏi trang trọng.
- Không bịa số liệu, feedback, đánh giá, giá, hạn, số chỗ, cam kết. Chữ người dùng đã chốt → giữ ý; rút gọn phải được đồng ý.
- Tiếng Việt có dấu đầy đủ; hạn chế tiếng Anh (chỉ giữ thuật ngữ quen của ngành). Chống rớt một chữ cuối dòng ở tiêu đề: `&nbsp;` giữa 2 chữ cuối.
- Tiêu đề không viết hoa toàn bộ (trừ khi brand.md yêu cầu).

## 4. Quy tắc HTML/CSS
- **Một file** `index.html`, CSS trong `<style>`; không JS framework, không thư viện ngoài, không script tracking (người dùng tự gắn trên nền tảng).
  JS nhỏ chỉ khi thật cần (vd đếm ngược theo hạn có thật) và trang vẫn đọc được khi JS tắt.
- Màu/font **chỉ** dùng biến `:root` từ Brand Kit (`ia landing tokens`). Màu nhấn dùng ít (nút, số, cụm từ khoá). Nền ưu tiên sáng, xen khối nhạt; khối tối chỉ khi brand.md cho.
- Bố cục: container ~1120px, lề 20px trên điện thoại; section cách nhau 72–96px; lưới thẻ bằng `grid` một cấp (`repeat(auto-fit,minmax(260px,1fr))`) —
  tránh grid lồng nhiều tầng. Chữ thân ≥16px trên điện thoại, nút cao ≥48px, chiều rộng đầy đủ trên điện thoại.
- Đúng 1 `<h1>`, tiêu đề section `<h2>`; `<title>` + `meta description`; ảnh có `alt`, `width/height` hoặc tỉ lệ để không nhảy trang; ảnh nén ≤300KB.
- **Tương thích khi dán vào trình dựng trang (LadiPage…)**: không dùng hiệu ứng hiện dần (`animation`, `opacity:0` chờ cuộn) — chữ có thể kẹt mờ;
  không dùng `<details>` (mũi tên tam giác xấu) → FAQ làm thẻ hiện sẵn câu trả lời; không dựa vào `display:none` trong media query để ẩn/hiện khối;
  menu điều hướng nhiều mục dễ vỡ trên điện thoại → header chỉ logo + nút.
- Icon: theo `brand.md` (có brand không muốn icon kiểu "AI") — không có hướng dẫn thì dùng số thứ tự 01/02/03 và viền nhấn thay icon.
- Không đặt thông tin cá nhân, ID tài khoản quảng cáo, mã pixel vào file.

## 5. Kiểm tra (`ia landing check` + mắt)
Máy chặn: thiếu viewport · tràn ngang trên điện thoại 390px · ảnh hỏng · không đúng 1 `<h1>` · thiếu `<title>`.
Máy cảnh báo: thiếu description/alt · nút chưa có đích · script ngoài · `<details>` · animation · chữ <13px · tương phản thấp.
Mắt soát (mở ảnh chụp):
- Màn đầu điện thoại: thấy nhãn + H1 + lời hứa + nút, không bị ảnh đẩy xuống.
- Phân cấp rõ: mỗi section một tiêu đề, cỡ chữ ≤3 mức, khoảng cách đều.
- Không chữ rớt một mình, không khối sát mép, thẻ trong một hàng cao bằng nhau.
- Màu đúng Brand Kit, màu nhấn không tràn lan; ảnh đúng nội dung khối chứa nó.
- Đọc lướt chỉ các `<h2>` → vẫn hiểu mạch trang.

## 6. Bàn giao
- `landing/LP/final/index.html` + `final/assets/`.
- **LadiPage**: tạo trang trống → phần tử HTML → dán nội dung; ảnh tải lên kho ảnh LadiPage rồi thay đường dẫn `assets/…`; form, pixel, chuyển hướng
  gắn trong builder. **Netlify**: kéo cả thư mục `final/` vào Netlify Drop.
- Sửa sau khi đã dán lên nền tảng: sửa file HTML (phiên bản mới) rồi dán lại — báo người dùng rằng dán lại có thể xoá chỉnh tay trong builder.

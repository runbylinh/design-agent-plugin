---
name: landing
description: >-
  Thiết kế landing page thành file HTML một trang theo Brand Kit — trang đăng ký (lead/form), bán khoá học/sản phẩm, sự kiện/workshop/webinar, giới thiệu dịch vụ — từ nội dung người dùng đưa, Brief của Agent Content, hoặc cấu trúc học được từ /design-agent:research. Chốt brief, đề xuất dàn ý section, viết HTML/CSS (màu, font Brand Kit, ưu tiên điện thoại, không thư viện ngoài), tự chụp máy tính + điện thoại và kiểm lỗi (tràn ngang, ảnh hỏng, tương phản, nút chưa có link), trình duyệt, quản lý phiên bản, bàn giao file HTML dán được vào LadiPage/Netlify. Dùng khi người dùng gõ /design-agent:landing, nói "thiết kế landing page", "làm trang đăng ký", "làm sales page", "landing cho khoá học/workshop", "code landing HTML", "sửa landing LP-…".
argument-hint: "[LP-ID | mô tả trang]"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/bin/ia:*), Bash(ia:*), Bash(cp:*), Bash(ls:*), Read, Write, Edit, Agent
---

# Thiết kế landing page (file HTML)

**Lệnh `ia`** = `${CLAUDE_PLUGIN_ROOT}/bin/ia`, chạy trong studio (không có → skill setup).
Đọc trước: `references/landing-page.md` (cấu trúc theo mục tiêu, viết chữ, quy tắc HTML, kiểm tra), `nguyen-tac.md` (mục Nội dung, Hình ảnh),
Brand Kit: `ia brand show` + `brand.md` (đặc biệt mục "Landing page" nếu có) + vài ảnh `anh-mau/`.
Đầu ra **chỉ là file HTML** — không tự đăng lên LadiPage/Netlify/hosting nào. Tiếng Việt, lời thường. Mỗi trang = mã `LP-YYMMDD-NN` trong `landing/`.

## 1. Nhận việc
Sửa trang cũ (`LP-…`) → `ia landing list` → `ia landing version LP --note "<góp ý>"` → sửa `vN/index.html` → mục 4.
Trang mới: gom brief theo `landing-page.md` §1 — mục tiêu, khách xem, lời hứa chính, Offer/giá/hạn, bằng chứng **có thật**, CTA + đích của nút
(link form, Zalo, hotline), nội dung gốc, ảnh có sẵn. Thiếu điều thật sự cần (đích CTA, giá, bằng chứng) → hỏi **một lượt**; không bịa.
Có phiên nghiên cứu landing (`ia research list`) → đọc "Cấu trúc tham khảo" trong `research/RS/phan-tich.md`.
`ia landing new --ten "<tên>" --muc-tieu <dang-ky|ban-hang|su-kien|gioi-thieu>` → điền `landing/LP/brief.md`.

## 2. Dàn ý (duyệt trước khi code khi trang ≥5 section)
Theo khung §2 của `landing-page.md` cho mục tiêu đã chọn: liệt kê section theo thứ tự, mỗi section 1 dòng (nội dung chính + cách trình bày).
Nội dung dài → gộp khối trùng ý, mỗi thẻ tiêu đề + 1 dòng (§3). Chữ người dùng đã chốt → giữ nguyên ý, chỉ rút gọn khi được đồng ý.
Trình dàn ý ngắn → **chờ người dùng gật** (trang nhỏ 3–4 section: làm luôn, nói rõ dàn ý trong lời trình).

## 3. Viết HTML
Sửa `landing/LP/v1/index.html` (khung đã có `:root` màu + font Brand Kit — xem `ia landing tokens`). Theo `landing-page.md` §4:
một file, CSS trong `<style>`, không JS/thư viện ngoài (trừ Google Fonts), ưu tiên điện thoại, đúng 1 `<h1>`, ảnh trong `vN/assets/` với `alt`,
mọi nút có `href` thật. Ảnh người/sản phẩm chỉ dùng ảnh người dùng/Media Assets cung cấp (`ia assets find`); thiếu ảnh khớp nội dung
→ bỏ ô ảnh hoặc báo cảnh còn thiếu, không lấp bằng ảnh lặp. Ảnh cần tách nền → `ia cutout`.

## 4. Tự kiểm
`ia landing check LP` → đọc lỗi/cảnh báo → **mở `vN/xem/dien-thoai-man-dau.png`, `dien-thoai.png`, `may-tinh-man-dau.png`, `may-tinh.png`**.
Soát bằng mắt theo `landing-page.md` §5 (màn đầu đủ H1 + lời hứa + nút, chữ rớt dòng, khoảng cách đều, nhịp nền, điện thoại đọc được).
Sửa → kiểm lại (tối đa 2 vòng tự sửa). Trang dài/quan trọng → có thể nhờ subagent soát độc lập (đưa đường dẫn ảnh chụp + brief, chỉ đọc).

## 5. Trình duyệt
Gửi đường dẫn ảnh chụp điện thoại + máy tính và `vN/index.html` (mở bằng trình duyệt được) + 2–4 dòng: cấu trúc trang, điểm cần quyết
(chữ dài, ảnh thiếu, link nút cần xác nhận, cảnh báo còn lại). **Dừng, chờ trả lời.**
- Góp ý → `ia landing version LP --note "<tóm tắt góp ý>"` → sửa bản mới → mục 4.
- Đồng ý → `ia landing approve LP --v N --xac-nhan "<nguyên văn lời người dùng>"` → bản cuối ở `landing/LP/final/`.
Góp ý lặp lại / mang tính quy tắc (màu nền, bo góc, icon, giọng văn) → đề xuất ghi vào `brand.md` mục "Landing page".

## 6. Bàn giao
Đưa đường dẫn `final/index.html` (+ `final/assets/`). Nhắc theo `landing-page.md` §6: dán vào LadiPage (HTML) hoặc kéo thư mục lên Netlify;
ảnh trong `assets/` cần tải lên nơi lưu ảnh của nền tảng rồi thay đường dẫn; form/pixel/tracking người dùng tự gắn trên nền tảng.

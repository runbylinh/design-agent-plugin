---
name: slide
description: >-
  Thiết kế slide thuyết trình / deck theo Brand Kit — deck đào tạo, Free Training, workshop, giới thiệu dịch vụ, báo cáo, pitch — từ dàn ý, tài liệu, ghi chú Notion/Google Doc hoặc deck cũ. Chốt trục câu chuyện và dàn slide (bìa · mục lục · chương · nội dung · số liệu · so sánh · kết), duyệt dàn ý, dựng từng slide bằng design.json 16:9, tự kiểm cả bộ, trình duyệt, xuất PNG + PDF + PPTX chữ sửa được để mở/nhập vào Canva hoặc PowerPoint. Dùng khi người dùng gõ /design-agent:slide, nói "làm slide", "thiết kế deck", "làm bài thuyết trình", "slide buổi …", "chuyển tài liệu này thành slide", "đưa deck lên Canva".
argument-hint: "[DS-ID | chủ đề / tài liệu]"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/bin/ia:*), Bash(ia:*), Bash(cp:*), Bash(ls:*), Read, Write, Edit, Agent
---

# Thiết kế slide / deck

**Lệnh `ia`** = `${CLAUDE_PLUGIN_ROOT}/bin/ia`, chạy trong studio (không có → skill setup).
Đọc trước: `references/formats/slide.md`, `nguyen-tac.md`, `design-json.md`, `qa.md`; Brand Kit (`ia brand show`, `brand.md`, `anh-mau/`, `ia template list`).
Quy trình giống skill **design** (nhận việc → dựng → tự kiểm → trình → duyệt → xuất → bàn giao); khác ở dàn ý và cách xuất. Tiếng Việt, lời thường.

## 1. Nhận việc + dàn ý (Duyệt dàn ý — bắt buộc khi ≥ 8 slide)
Gom: mục đích buổi/tài liệu, người xem, thời lượng, nội dung nguồn (tài liệu, Notion, deck cũ — đọc hết), ảnh/ảnh chụp màn hình có sẵn, CTA cuối.
Theo `formats/slide.md` §1: chốt **trục câu chuyện** (1 câu) và **bảng dàn slide**: số · loại (bìa/chương/nội dung/số liệu/so sánh/ảnh/kết) · tiêu đề · ý chính · hình ảnh cần.
Trình bảng → **chờ người dùng gật** rồi mới dựng. Nội dung người dùng đã viết → giữ nguyên ý, chỉ chia slide/rút gọn khi được đồng ý.
`ia job new --loai slide --ten "<tên deck>"` → ghi dàn ý vào `jobs/DS/input/design-brief.md`.

## 2. Dựng
Một `design.json`, mỗi slide một trang (`id` = `s01`, `s02`…), `canvas.preset` = `slide_16x9`.
Bố cục: `slide-bia`, `slide-chuong`, `slide-noi-dung`, `slide-noi-dung-anh`, `slide-hai-cot`, `slide-ket` + bố cục chung có biến thể 16:9
(`so-lieu`, `danh-sach`, `tieu-de-giua`…) + bố cục riêng của brand (`ia layouts`). Chữ đã chốt → `content_locked: true`.
Thành phần lặp mọi slide (số trang, logo, tên buổi) → đặt cùng vị trí ở mọi slide nội dung. Biểu đồ: `formats/bieu-do.md` (bắt buộc `source`).
Ảnh chụp màn hình: phóng gần hết vùng ảnh, không viền khung lòe loẹt. Deck dài (≥ 20 slide) → dựng 4–5 slide đại diện (bìa, chương, nội dung, số liệu, kết) trình trước, duyệt hướng rồi mới dựng hết.

## 3. Tự kiểm + trình
`ia render DS` → mở `xem-nhanh.png` (cả bộ) và vài slide `out/*.png` cỡ thật. Soát `formats/slide.md` §4. Bỏ qua cảnh báo "xem trên điện thoại" nếu deck chỉ trình chiếu.
Deck ≥ 10 slide → gọi subagent `design-qa` (truoc-duyet). Trình: đường dẫn `xem-nhanh.png` + thư mục `out/` + điểm cần quyết. **Dừng, chờ trả lời.**
Góp ý → `ia version new DS --note "…"` → sửa → dựng lại. Đồng ý → `ia approve DS --v N --xac-nhan "<nguyên văn>"`.

## 4. Xuất + Canva
`ia export DS --dinh-dang png,pdf,pptx` → `approved/DS.pdf` (cả bộ), `approved/DS.pptx` (chữ sửa được, nền là ảnh), PNG từng slide.
Người dùng muốn sửa tiếp trên Canva → theo `formats/slide.md` §5: tải PPTX lên Canva (Claude in Chrome: Canva → Tải lên → `file_upload` vào ô chọn file),
mở thiết kế Canva tạo ra, kiểm font (Canva nhận thường/đậm; Black/SemiBold → Bold), báo link Canva. Không tự chia sẻ công khai.
Bàn giao Drive như skill design mục 6 (`ia publish`, `ia link`).

---
name: research
description: >-
  Nghiên cứu mẫu thiết kế mới nhất rồi học theo và đóng gói thành bố cục/mẫu dùng lại — quét thư viện thiết kế (Pinterest, Behance, Dribbble, Canva, Figma Community), quảng cáo và fanpage cùng ngành (Meta Ads Library, Facebook, Instagram), hoặc link/ảnh người dùng gửi; lưu ảnh mẫu kèm nguồn, ghép moodboard, phân tích từng mẫu (bố cục, phân cấp chữ, màu, xử lý ảnh, mật độ chữ, CTA), rút ra mẫu lặp và xu hướng, đề xuất 3–5 hướng hợp Brand Kit, dựng 3–5 bản thử cho duyệt, rồi lưu bố cục mới vào Brand Kit + mẫu đã duyệt để /design-agent:design dùng. Dùng khi người dùng gõ /design-agent:research, nói "tìm template mới", "xem xu hướng thiết kế", "research mẫu carousel/thumbnail/poster/quảng cáo", "học style này", "đối thủ đang thiết kế thế nào", "làm mới bộ template", "đóng gói style này thành mẫu", "tham khảo landing page".
argument-hint: "[loại ấn phẩm | chủ đề | link]"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/bin/ia:*), Bash(ia:*), Bash(cp:*), Bash(ls:*), Read, Write, Edit, Agent, WebSearch
---

# Nghiên cứu mẫu thiết kế → học theo → đóng gói

**Lệnh `ia`** = `${CLAUDE_PLUGIN_ROOT}/bin/ia`, chạy trong studio (thư mục có `image-studio.json`; không có → skill setup).
Đọc trước: `references/research-mau.md` (nguồn, khung phân tích, cách chụp mẫu, đóng gói), `nguyen-tac.md` (quy tắc 6: chỉ học cấu trúc),
`design-json.md` (bố cục), Brand Kit (`ia brand show` + `brand.md` + vài ảnh `anh-mau/`).
Tiếng Việt, lời thường. Mỗi phiên = một mã `RS-YYMMDD-NN` trong `research/`.

## 1. Chốt đề bài (hỏi một lượt nếu thiếu)
- **Loại ấn phẩm**: carousel, thumbnail, ảnh FB/IG, quảng cáo, poster, ảnh bìa, story, landing page.
- **Brand + mục đích**: kiến thức, bán hàng, sự kiện, tuyển sinh… · **Ngành / đối thủ** (nếu xem quảng cáo, fanpage).
- **Nguồn**: thư viện thiết kế · quảng cáo & fanpage ngành · link/ảnh người dùng gửi (mặc định: cả ba nếu người dùng không nói).
- **Muốn học gì**: bố cục mới, cách trình bày số liệu, cách dùng ảnh người, cả hệ thống…
`ia research new --ten "<đề bài ngắn>" --loai <loại>` → ghi đề bài vào mục 1 của `research/RS/phan-tich.md`.

## 2. Thu mẫu (mặc định 12–20 mẫu, tối đa ~30)
Theo `research-mau.md` §1–2. Duyệt web bằng **Claude in Chrome** (load công cụ một lần); Meta Ads Library có thể qua connector quảng cáo (`ads_library_search`) nếu có.
Xu hướng chung của năm/ngành: WebSearch vài bài "design trends" mới nhất làm bối cảnh (ghi link).
Mỗi mẫu chọn được: chụp đúng vùng thiết kế (zoom `save_to_disk`, scale 1) → `ia research add RS <file> --url <link gốc> --nguon <nền tảng> --ghi-chu "<vì sao chọn>"`.
Link/ảnh người dùng gửi: ảnh → `ia research add` thẳng; link → mở bằng Chrome rồi chụp như trên.
Bỏ mẫu: chữ không đọc được, ảnh quá nhỏ, trùng ý với mẫu đã có, khác hẳn loại ấn phẩm.
Xong → `ia research moodboard RS` → mở `moodboard.png` xem lại cả bộ.

## 3. Phân tích
Mở **từng ảnh** trong `research/RS/mau/`, phân tích theo khung `research-mau.md` §3, ghi vào `phan-tich.md` mục 2–4:
nguồn · phân tích từng mẫu (ngắn) · bảng mẫu lặp & xu hướng (đang nổi / phổ biến / bão hoà, hợp brand không).
Bộ ≥15 mẫu → có thể giao subagent phân tích song song theo nhóm nguồn, nhưng **tổng hợp xu hướng do bộ điều phối làm**.

## 4. Trình báo cáo (Duyệt 1) — dừng, chờ người dùng chọn
Gửi đường dẫn `moodboard.png` + `phan-tich.md` và tóm tắt trong chat:
- 3–5 xu hướng/mẫu lặp đáng chú ý, mỗi cái 1 dòng + số mẫu minh hoạ (#03, #07…).
- **3–5 hướng áp dụng cho brand** (`research-mau.md` §4): tên ngắn · học từ mẫu số … · dùng cho ấn phẩm nào · khác gì bố cục đang có.
Hỏi: chọn hướng nào để dựng thử? (có thể chọn nhiều). **Không dựng hàng loạt trước khi người dùng chọn.**

## 5. Dựng thử (3–5 bản) — theo Brand Kit, nội dung thật
Mỗi hướng được chọn:
1. Viết file bố cục `research/RS/thu/<ten-huong>.json` theo `research-mau.md` §5 (cấu trúc giống `templates/layouts/*.json`, vùng tỉ lệ 0–1,
   đủ biến thể tỉ lệ cần dùng) → `ia layout check <file>`.
2. Lưu tạm để dựng: `ia layout save <file> --ten <ten-huong> --tu RS` (bố cục vào `Brand Kit/thanh-phan/layouts/`; chưa duyệt thì tên có hậu tố `-thu`).
3. `ia job new --loai <loại> --ten "Thử style <hướng> (RS-…)"` → `design.json` dùng `"layout": "<ten-huong>"`, chữ thật của brand (bài gần đây, không viết chữ mẫu ngoặc vuông)
   → `ia render DS` → mở ảnh, tự sửa tối đa 2 vòng (như skill design mục 4).
Trình cả bộ thử cạnh mẫu gốc tương ứng (ghi rõ "học từ #05 + #11"), nói điểm khác so với mẫu gốc. **Dừng, chờ duyệt (Duyệt 2).**
Góp ý → sửa bố cục/design.json → dựng lại. Hướng bị loại → xoá bố cục `-thu` của hướng đó khỏi Brand Kit.

## 6. Đóng gói (sau khi người dùng đồng ý)
Theo `research-mau.md` §6:
- Bố cục được duyệt: `ia layout save <file> --ten <tên chính thức> --tu RS` (bỏ hậu tố `-thu`, xoá bản `-thu`).
- Bản thử được duyệt: `ia approve DS --v N --xac-nhan "<nguyên văn>"` → `ia template save DS --ten <tên> --mo-ta "…" --cho-doi hook,sub,…` → vào thư viện mẫu.
- Quy tắc học được (màu nhấn, cách dùng ảnh, mật độ chữ…): đề xuất thêm vào `brand.md` mục "Style đã học" → chỉ ghi khi người dùng đồng ý.
- Ghi mục 6 `phan-tich.md` → `ia research done RS --goi "<bố cục…, mẫu…>"`.
Kết: liệt kê tên bố cục/mẫu mới, cách gọi lại ("làm carousel theo mẫu <tên>"), đường dẫn moodboard + phân tích.

## Landing page
Loại = landing: thu ảnh chụp **cả trang** (máy tính + điện thoại) và từng section đáng học; phân tích theo `research-mau.md` §3b
(thứ tự section, hero, cách đặt bằng chứng/Offer/CTA, form). Đóng gói = ghi "Cấu trúc tham khảo" vào `phan-tich.md` để skill `landing` dùng
— không tạo bố cục ảnh.

---
name: design
description: >-
  Thiết kế ấn phẩm tĩnh mới theo Brand Kit — thumbnail YouTube, carousel nhiều trang, ảnh Facebook/Instagram, ảnh quảng cáo và biến thể thử nghiệm, poster workshop/sự kiện/mở bán, ảnh bìa kênh, biểu đồ/case study, đồ hoạ cho video (Graphic Pack theo Scene ID) — từ yêu cầu trực tiếp (chữ, ảnh thô, ý tưởng, ảnh tham khảo) hoặc từ Brief ảnh / Script video đã duyệt của Agent Content (TASK-/CT-). Tự tìm logo/ảnh trong Media Assets, tách nền, dàn trang, tự kiểm, trình duyệt, xuất PNG/JPG/PDF, đưa lên Google Drive và cập nhật 04 Production. Dùng khi người dùng gõ /image-agent:design, nói "thiết kế…", "làm thumbnail/carousel/poster/ảnh bìa/ảnh quảng cáo", "làm ảnh cho CT-…/TASK-…", "dựng đồ hoạ cho video", "vẽ biểu đồ", "làm bộ ảnh chiến dịch".
argument-hint: "[TASK-ID | CT-ID | mô tả]"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/bin/ia:*), Bash(ia:*), Bash(base64:*), Read, Write, Edit, Agent
---

# Thiết kế mới

**Lệnh `ia`** = `${CLAUDE_PLUGIN_ROOT}/bin/ia`, chạy trong studio (thư mục có `image-studio.json`; không có → skill setup).
Đọc trước: `references/nguyen-tac.md`, `dieu-phoi.md`, `design-json.md`, `qa.md`; định dạng: `references/formats/<loại>.md`.
Tiếng Việt, lời thường. Claude **dàn trang bằng design.json**, không vẽ pixel; AI tạo ảnh chỉ cho nền/hoạ tiết, không bao giờ viết chữ.

## 1. Nhận việc
Theo `dieu-phoi.md` §1 xác định đầu vào và Use Case.
- **Trực tiếp:** `ia job new --loai <loại> --ten "<tên ngắn>"`. Brief/script dán tay → lưu `jobs/DS/input/brief.md` → `ia brief --file … --job DS`.
- **Từ Agent Content (TASK-):** content-agent ở chế độ Google Sheets → pull phiếu trước (theo ket-noi-google.md của content-agent).
  `ia job new --loai … --ten … --task TASK-… --ct CT-…` → `ia brief TASK-… --job DS` → `ia sync DS nhan` (push nếu content-agent yêu cầu).
  Chữ chưa duyệt → chỉ bản thử (nói rõ). Nội dung có vấn đề → `hop-dong-ban-giao.md` §3.
- **Script video (D14):** `ia brief … --job DS` → `ia asset-list DS` → Claude đọc script, sửa danh sách → **trình bảng Graphic Asset List, chờ duyệt** → mới dựng.
Thiếu thông tin thật sự cần (`dieu-phoi.md` §2) → hỏi một lượt. Ghi Design Brief vào `jobs/DS/input/design-brief.md` (việc nhỏ thì bỏ qua).

## 2. Brand + tài nguyên
`ia brand show` + đọc `brand.md`, xem vài ảnh trong `anh-mau/`, `ia template list` (có mẫu hợp → `ia template use`, 1 phương án).
Tài nguyên: `ia assets find <từ khoá>` → không có thì Drive theo `media-assets.md` (Asset Retrieval). Ảnh người dùng gửi trong chat/đường dẫn → chép vào `jobs/DS/input/`.
Mỗi ảnh: `ia inspect <ảnh>` + **mở ảnh xem** → quyết định vai trò: *chủ thể cần tách* · *nền tràn* · *ảnh trong khung* · *ảnh tư liệu*.
Chỉ chủ thể mới `ia cutout <ảnh> --job DS` → mở `*-kiem-vien.png`. Viền xấu → `nguyen-tac.md` bảng "Khi công cụ không có / lỗi".
Ảnh quá nhỏ/mờ → báo trước khi dựng. Higgsfield (upscale, remove_background, tạo nền) **chỉ khi người dùng cho phép gửi ảnh**.

## 3. Dàn trang
Viết `jobs/DS/v1/design.json` (hoặc `v1/huong-a|b|c/design.json` khi cần 2–3 hướng — `dieu-phoi.md` §3).
- Chọn khổ (`ia presets`) và bố cục (`ia layouts`) theo `formats/<loại>.md`. Bố cục chưa đủ → thêm thành phần có `box`, hoặc `html` khi thật cần.
- Chữ từ Brief đã duyệt / người dùng đưa: `content_locked: true`. Nhấn bằng `**…**`, xuống dòng bằng `\n` cho đẹp — không đổi chữ.
- Biểu đồ: `formats/bieu-do.md`, luôn có `source`. Biểu tượng: `ia icons find <từ tiếng Anh>`.
- Ảnh tham khảo (D07): mô tả cấu trúc bố cục của ảnh mẫu bằng lời trong design-brief, rồi dựng bằng Brand Kit — không lấy hình của mẫu.

## 4. Dựng + tự kiểm (QA lần 1)
`ia render DS` → đọc lỗi/cảnh báo → **mở `out/*.png`, `xem-dien-thoai.png`, (carousel) `xem-nhanh.png`, (nhiều hướng) `so-sanh-huong.png`**.
Lỗi máy hoặc lỗi nhìn thấy → sửa design.json → render lại (tối đa 2 vòng tự sửa). Việc lớn (carousel ≥5 trang, bộ chiến dịch, Graphic Pack, quảng cáo)
→ gọi subagent `design-qa` với đường dẫn plugin + studio + DS, sửa theo báo cáo.

## 5. Trình duyệt
Gửi ảnh (đường dẫn file để người dùng mở) + 2–4 dòng: đã làm gì, dùng tài nguyên nào, điểm cần người dùng chú ý / quyết định
(hướng nào, chữ dài, ảnh thiếu chất lượng, font thay thế). **Dừng, chờ trả lời.**
- Góp ý → `ia version new DS [--tu vN --huong b] --note "<tóm tắt góp ý>"` → sửa v mới → render → trình lại.
- Đồng ý → `ia approve DS --v N [--huong x] --xac-nhan "<nguyên văn lời người dùng>"`.
Góp ý lặp lại / mang tính quy tắc → đề xuất thêm vào Brand Kit `rules`.

## 6. Xuất + QA lần 2 + bàn giao (mặc định, không hỏi lại)
`ia export DS [--dinh-dang …] [--max-kb …]` (tự chạy `ia check`) → mở `approved/xem-dien-thoai/` xem lần cuối.
Đồ hoạ video: viết `approved/huong-dan-dat.md` (`formats/video-graphic.md`).
`ia publish DS` → làm theo các bước lệnh in ra (`media-assets.md` Asset Publishing) → `ia link DS --url … --kiem '…'`.
Có phiếu → `ia sync DS xuat-thu` (+ push của content-agent). Chưa có link hợp lệ → nói rõ "Chờ upload", không báo đã bàn giao.
Kết: link Drive (hoặc đường dẫn `approved/`), file nào, trạng thái phiếu, việc còn chờ người dùng.

## Bộ chiến dịch, biến thể, nhiều job
D09: `dieu-phoi.md` §5. D10: `formats/quang-cao.md`. Nhiều job độc lập (≥3) cần dựng song song → có thể giao subagent, mỗi subagent một DS,
nhưng **trình duyệt và approve do bộ điều phối làm**.

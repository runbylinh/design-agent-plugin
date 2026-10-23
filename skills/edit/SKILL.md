---
name: edit
description: >-
  Sửa thiết kế đã có của Agent 02 Ảnh — mở lại job cũ (DS-/CT-/tên), sửa đúng phần được yêu cầu và giữ nguyên thành phần người dùng chốt (khoá nội dung, khoá cách thể hiện); hoặc nhận một ảnh PNG/JPG cũ không có file nguồn, phân tích bố cục và dựng lại phần cần chỉnh. Xử lý cả khi Brief/Script nguồn của Agent Content đã đổi sau khi thiết kế bắt đầu. Dùng khi người dùng gõ /image-agent:edit, nói "sửa ảnh…", "giữ nguyên … chỉ đổi …", "đổi màu nền / tăng chữ / thay logo", "mở lại ảnh tháng trước để sửa", "ảnh cũ này sửa lại bố cục", "script đổi rồi, cập nhật đồ hoạ".
argument-hint: "[DS-ID | CT-ID | ảnh]"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/bin/ia:*), Bash(ia:*), Read, Write, Edit, Agent
---

# Sửa thiết kế (D05, D15)

**Lệnh `ia`** = `${CLAUDE_PLUGIN_ROOT}/bin/ia`. Đọc: `references/nguyen-tac.md`, `design-json.md` (mục Khoá), `qa.md`.

## 1. Tìm đúng bản
`ia job find <DS | CT | TASK | từ khoá>` → `ia job show DS`. Mặc định sửa từ **bản đã duyệt** (`ban_duyet`), không phải bản nháp mới nhất — nói rõ đang sửa từ v nào.
Job từ Agent Content → `ia source-check DS` trước (nguồn đổi → mục 4).

## 2. Khoanh phạm vi
Ghi ra (và nhắc lại cho người dùng một dòng): **đổi gì** · **giữ nguyên gì**.
- "Giữ nguyên hình người, logo, nội dung" → các thành phần đó: `content_locked: true` + `style_locked: true` (giữ `box/slot/style/src`).
- "Giữ chữ nhưng dàn lại hoàn toàn" → chỉ `content_locked`.
`ia version new DS --tu v<duyệt> --note "<đổi gì / giữ gì>"` → sửa design.json bản mới **chỉ phần được yêu cầu**.
Trước khi render: so design.json mới với bản gốc — thành phần `style_locked` phải y nguyên (tự kiểm, máy không kiểm phần này).

## 3. Chỉ có ảnh PNG/JPG (không có design.json)
Nói trước với người dùng: **sẽ dựng lại gần giống, không trùng từng pixel**; thiếu file font gốc thì chữ có thể khác.
1. `ia job new --loai … --ten "Sửa: …"` → chép ảnh cũ vào `input/`. Mở ảnh, ghi lại: khổ, bố cục (vị trí từng khối theo tỉ lệ), chữ (chép đúng từng ký tự), màu (`ia brand colors <ảnh>`), font đoán được.
2. Thành phần cần giữ là hình (người, sản phẩm, logo) → `ia cutout` từ ảnh cũ (hoặc lấy logo gốc từ Brand Kit — ưu tiên file gốc nét hơn).
3. Viết design.json tái tạo ảnh cũ (v1) → render → đặt cạnh ảnh cũ so sánh → chỉnh tới khi gần giống → rồi mới làm phần sửa ở v2.
   Như vậy người dùng thấy rõ v1 = bản dựng lại, v2 = bản đã sửa.

## 4. Nguồn đổi (D15)
`ia source-check DS` báo phần sửa/thêm/bỏ và đồ hoạ bị ảnh hưởng. Không tự thay file đã duyệt/đã bàn giao/đang được Agent Video dùng.
Trình người dùng: giữ (không ảnh hưởng) · sửa (cảnh/trang đổi) · thêm · bỏ. Đồng ý → `ia brief … --job DS` (khoá nguồn mới) →
`ia lock DS --reset --xac-nhan "<lời người dùng>"` → `ia version new` → sửa đúng các trang/cảnh đó → render → duyệt → xuất → bàn giao lại, ghi chú "thay bản cũ".

## 5. Dựng, duyệt, xuất
Như skill design mục 4–6: render → mở ảnh → (việc lớn) `design-qa` → trình (nói rõ đã đổi gì, giữ gì) → approve → export → publish → link → sync.

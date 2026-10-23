---
name: setup
description: >-
  Cài và thiết lập Agent 02 Ảnh — cài môi trường dựng ảnh trên máy (không cần mật khẩu), tạo studio ảnh, đọc Brand Guideline (PDF/link/ảnh) thành Brand Kit (màu, font, logo, quy tắc nên/không, tinh thần thương hiệu), nối Brand Kit có sẵn của video-edit, dựng thử 2–3 mẫu để duyệt, thư viện mẫu đã duyệt, kết nối Media Assets trên Google Drive (kiểm quyền đọc/ghi) và workspace Agent Content. Dùng khi người dùng gõ /image-agent:setup, nói "cài agent ảnh", "đây là brand guideline", "học brand này", "thêm brand mới", "nối Drive / Media Assets", "kiểm tra agent ảnh".
argument-hint: "[thư mục studio | brand]"
allowed-tools: Bash(${CLAUDE_PLUGIN_ROOT}/bin/ia:*), Bash(ia:*), Read, Write, Edit
---

# Thiết lập Agent 02 Ảnh

**Lệnh `ia`** = `${CLAUDE_PLUGIN_ROOT}/bin/ia`. Đọc trước: `${CLAUDE_PLUGIN_ROOT}/references/nguyen-tac.md`, `brand-kit.md`, `media-assets.md`.
Luôn nói tiếng Việt, lời thường, không thuật ngữ kỹ thuật khi không cần.

## 1. Môi trường (mỗi máy một lần)
`ia doctor`. Có ❌ → `ia setup` (chạy nền, vài phút: Python, Chromium, font Be Vietnam Pro, bộ biểu tượng). Model tách nền tự tải ở lần tách đầu (~170MB).
Windows: `ia setup` gọi PowerShell — nếu lỗi, báo nguyên văn lỗi cho người dùng.

## 2. Studio
Hỏi gọn (một lượt): đặt studio ở đâu (mặc định `~/Image-Studio`), brand tên gì, đã có Brand Kit bên video-edit chưa.
- Có Brand Kit video-edit: `ia studio init <thư mục> --brand-kit <…/video-studio/brand-kit/<brand>> --brand <brand>` (dùng chung, không chép).
- Chưa có: `ia studio init <thư mục>` → `cd` vào → `ia brand init <brand>`.
Brand thứ hai trở đi: `ia brand init <brand> [--tu <thư mục>]`.

## 3. Brand Guideline → Brand Kit
Theo `references/brand-kit.md` mục "Đọc guideline → Brand Kit": đọc guideline, `ia brand colors`, ghi brand.json + brand.md, logo nền sáng/tối,
font (`ia font get` / xin file), quy tắc nên/không cụ thể, ảnh mẫu đúng chất vào `anh-mau/`. Điều suy ra → ghi **[CẦN XÁC NHẬN]** và hỏi.
`ia brand check` đến khi ✅.
Báo người dùng bản tóm tắt: "Đã học xong: màu …, font …, logo …, tinh thần …" + những điểm cần xác nhận.

## 4. Dựng thử để chốt tinh thần
Dựng 2–3 mẫu bằng skill design (nội dung thật của brand, ví dụ một thumbnail, một trang carousel, một ảnh chỉ chữ).
Người dùng góp ý → sửa → thêm quy tắc vào `rules`/brand.md. Duyệt → `ia approve` → `ia template save <DS> --ten <tên> --cho-doi <id…>`.

## 5. Google Drive — Media Assets + Sheet "Hệ thống Design ảnh"
Theo `references/media-assets.md`. Hỏi link thư mục **Media Assets** (trong thư mục brand của Content Workspace; bộ mẫu đã có sẵn cây thư mục + Sheet).
1. Connector Google Drive: `search_files parentId = '<Media Assets>'` → thư mục `01 Ảnh` → trong đó tìm Sheet "… | Hệ thống Design ảnh …", `01 Source thô`, `02 Final` (bộ cũ chưa có `01 Ảnh` → tìm thẳng trong Media Assets);
   trong đó tìm `07 Theo việc`, `00 Mẫu đã duyệt`. Thiếu thư mục nào → tạo đúng tên trong media-assets.md (chỉ tạo mới, không sửa/chuyển file có sẵn).
   Thiếu Sheet → `create_file` mimeType spreadsheet tên "<BRAND> | Hệ thống Design ảnh" rồi bước 3 tạo cấu trúc.
2. `ia sheet connect --url <link Sheet> --media-assets <link Media Assets> --source-id <id 01 Source thô> --final-id <id 02 Final> --theo-viec-id <id 07 Theo việc> --mau-id <id 00 Mẫu đã duyệt>`
3. Sheet mới, trống → `ia sheet init-plan` → chạy `update_spreadsheet` + các `update_values` trong `.tracker/init-plan.json`. Sheet copy từ bộ mẫu → bỏ qua.
4. `ia sheet pull-plan` → đọc 4 tab → `ia sheet pull <Tab> --file …` (thiếu cột → báo người dùng).
5. Kiểm quyền: đọc được Sheet (bước 4), **ghi thử** một file chữ nhỏ `_kiem-thu-agent-anh.txt` vào `02 Final` (`create_file` textContent). Thiếu quyền nào → báo chính xác.
   File thử: báo người dùng để họ xoá; không tự xoá vĩnh viễn.
6. `ia drive setup --che-do thu-cong`. Máy có Google Drive for Desktop và người dùng muốn tự động → `--che-do dong-bo --sync-root <Media Assets trên máy>` rồi `ia assets scan <…/01 Source thô>`.
7. Ảnh thô đang có trong `01 Source thô` → đăng ký vào tab 02 Source: `search_files` từng nhóm → `ia assets add - --drive-id <id> --nhom "<Nhóm>" --ten … --tag … --quyen …`
   (hỏi người dùng tag tên người cho ảnh Người, quyền dùng) → `ia sheet push`.
Nói rõ giới hạn: connector chỉ chở ảnh ~20KB → ảnh thành phẩm người dùng kéo vào thư mục Final agent tạo sẵn.
Connector Google Drive / Google Sheets chưa kết nối → báo cần bật trong Claude (Settings → Connectors); agent vẫn dựng ảnh được, chỉ thiếu phần Drive/Sheet.

## 6. Agent Content (tuỳ chọn)
Người dùng có workspace Agent Content → `ia content connect <thư mục có content-studio.json>` → `ia content info` kiểm.
Content-agent dùng connector Google Sheets → khi cần đọc/ghi phiếu phải theo vòng pull/push của content-agent (`references/ket-noi-google.md` trong plugin content-agent).

## 7. Kết thúc
`ia doctor` + `ia brand check` + `ia status`. Tóm tắt: studio ở đâu, Brand Kit nào, Drive chế độ gì, có nối Agent Content không, việc còn thiếu.

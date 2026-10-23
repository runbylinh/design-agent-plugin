# Media Assets trên Google Drive — lấy tài nguyên & đưa thành phẩm lên

Media Assets (Drive, trong cây thư mục brand của Content Workspace) là kho chung của Agent Content – Ảnh – Video.
Nhóm logic (dùng thư mục có sẵn nếu tương đương, không tạo lại):
`Brand Assets/` (logo, font) · `Design Elements/` (icon, khung, nền) · `Source Media/` (ảnh người, sản phẩm, ảnh đã tách nền) · `Approved Designs/` (thành phẩm, mẫu).

## Giới hạn đã đo (2026-10-23)
Connector Google Drive của Claude chở **file nhị phân qua base64 trong hội thoại**: ảnh 2KB upload + tải lại khớp checksum; ảnh 28KB đã vượt trần
→ **trần thực tế ~20KB/file ảnh**. Không có MD5. File chữ (design.json, manifest.json, .md) ghi bằng `textContent` thì ổn.
Hệ quả: connector dùng để **tìm, lấy ID/link, tạo thư mục, ghi file chữ**. Ảnh thật đi bằng đồng bộ (Drive for Desktop) hoặc người dùng kéo thả.

Chế độ (`ia drive setup`):
- `thu-cong` (mặc định): như trên.
- `dong-bo`: Media Assets đồng bộ xuống máy → `ia assets scan <thư mục>` đăng ký; `ia publish` chép thẳng.

## Asset Retrieval (trước khi dựng)
1. `ia assets find <từ khoá> [--loai logo|element|anh|mau]` — Brand Kit + registry `_assets.json` (+ thư mục đồng bộ).
2. Không thấy trên máy → connector `search_files` trong thư mục Media Assets (`title contains '…'`, `parentId = '…'`, `mimeType contains 'image/'`),
   ưu tiên Brand → loại → tên → tag → đã duyệt. **Không quét cả Drive.**
3. Thấy file trên Drive:
   - ≤ 20KB (logo nhỏ, icon) → có thể `download_file_content` → ghi bằng `base64 -D` vào `jobs/DS/assets/` → kiểm mở được.
   - Lớn hơn → nhờ người dùng tải về / kéo vào chat hoặc `jobs/DS/input/` (nói rõ tên file + link Drive). Chế độ dong-bo: dùng thẳng đường dẫn.
   - Đăng ký: `ia assets add <file> --loai … --tag … --drive-id <id>` để lần sau tìm nhanh.
4. Nhiều ảnh gần giống → xem ảnh, đưa 2–4 lựa chọn. Không có ảnh phù hợp → **báo thiếu**, không chọn ảnh không liên quan.
5. Ảnh người: phải có tag tên người trong registry (máy không nhận diện khuôn mặt) — thiếu tag thì hỏi người dùng ảnh nào là ai.

## Asset Publishing (sau khi duyệt) — mặc định, không hỏi lại
`ia export` → `ia check` (QA sau xuất) → `ia publish DS` → làm đúng các bước lệnh in ra:
1. Thư mục `Approved Designs/<BRAND>/<YYYY-MM>/<DS>/`: `search_files` từng cấp, thiếu thì `create_file` (mimeType folder, parentId cấp trên).
   Không đặt `inheritedPermissionsDisabled`, không chia sẻ.
2. File chữ (`design.json`, `manifest.json`, `source.html`, `huong-dan-dat.md`) → `create_file` với `textContent`, `contentMimeType` đúng,
   `disableConversionToGoogleType: true`.
3. Ảnh/PDF → nhờ người dùng kéo từ `jobs/DS/ban-giao/` vào thư mục (gửi link thư mục). Chế độ dong-bo: đã chép, chờ đồng bộ.
4. `search_files` `parentId = '<id>'` → lấy `title` + `fileSize` → `ia link DS --url <viewUrl thư mục> --folder-id <id> --kiem '{"tên": fileSize, …}'`.
   Lệch / thiếu → giữ Chờ upload, báo đúng file nào.
5. Có phiếu TASK → `ia sync DS xuat-thu`.
Bản nháp/bản thử: chỉ ở máy (`jobs/`), không đưa lên Approved Designs.

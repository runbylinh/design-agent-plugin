# Media Assets (Drive) + Sheet "Hệ thống Design ảnh"

Media Assets nằm trong thư mục brand của Content Workspace (bộ mẫu: `Content Workspace - Template/Media Assets`). Học viên copy cả bộ mẫu.

```
Media Assets/
├── 01 Ảnh/                                  ← Agent 02 (plugin này)
│   ├── <BRAND> | Hệ thống Design ảnh        Google Sheet — quản lý Brief, ảnh thô, thành phẩm, quá trình
│   ├── 01 Source thô/
│   │   ├── 01 Logo & nhận diện/  02 Người/  03 Sản phẩm - Dịch vụ/  04 Bối cảnh/
│   │   ├── 05 Đồ hoạ & thành phần/  06 Tham khảo/
│   │   └── 07 Theo việc/<DS-…>/             ảnh thô chỉ dùng cho một việc
│   └── 02 Final/
│       ├── 00 Mẫu đã duyệt/
│       └── <YYYY-MM>/<DS-… · tên>/          ảnh thành phẩm + _nguon/ (design.json, manifest.json, source.html)
└── 02 Video/                                ← Agent 03 (plugin video-edit) — Agent 02 chỉ đọc footage/khung hình khi làm thumbnail, đồ hoạ video
```
Bản nháp chỉ ở máy (`jobs/`). Final chỉ chứa bản đã duyệt.

## Sheet (cấu trúc: `templates/tracker.json`; tiêu đề cột dòng 3; agent tìm cột theo tên)
| Tab | Mỗi dòng | Agent ghi khi |
|---|---|---|
| 01 Brief & Việc | 1 DS | `job new` (tạo dòng) · `brief` (Brief + chữ đã duyệt) · `render`/`version`/`approve`/`publish`/`link` (trạng thái, bản, người/ngày duyệt, link) |
| 02 Source | 1 AS | `assets add` |
| 03 Recap thiết kế | 1 bước | `render` (Dựng), `version new` (Sửa + góp ý), `approve` (Duyệt), `export` (Xuất), `publish`/`link` (Bàn giao), `source-check` (Nguồn đổi), `ia sheet recap` (kết quả design-qa) |
| 04 Tiêu chuẩn | 1 loại ấn phẩm | không ghi — để người đọc hiểu agent kiểm theo gì |
Brief từ Agent 01: chép sang với nhãn `[CHỈ ĐỌC — sửa ở Agent Content · bản … · mã …]`. Không sửa ô đó; chữ cần đổi → Agent 01.
Agent chỉ ghi **ô nó đổi**, không ghi đè cả dòng — cột người dùng tự ghi (Ghi chú, Yêu cầu riêng…) giữ nguyên.

## Vòng đọc/ghi Sheet (connector Google Sheets của Claude)
1. **Đầu phiên / khi người dùng vừa sửa Sheet:** `ia sheet pull-plan` → `get_values` từng vùng → lưu JSON kết quả ra file → `ia sheet pull <Tab> --file …`.
2. Làm việc bình thường — các lệnh `ia` tự xếp hàng thay đổi (`📝 Sheet: n lệnh ghi đang chờ`).
3. **Sau mỗi nhóm việc, trước khi trình duyệt và trước khi kết thúc:** `ia sheet push` → chạy từng `update_values` trong `calls` → `ia sheet push --xong <n>`. Còn lệnh → push tiếp. Tối đa ~12 lệnh mỗi lượt.
Chưa nối Sheet → agent vẫn chạy, chỉ bỏ qua phần Sheet; nhắc người dùng setup.
Không pull khi còn lệnh chưa push (sẽ mất thay đổi).

## Sheet mới (học viên vừa copy bộ mẫu có sẵn Sheet → bỏ qua)
`ia sheet connect --url <link Sheet>` → `ia sheet init-plan` → chạy `update_spreadsheet` (requests trong `.tracker/init-plan.json`) rồi từng `update_values`.
Chỉ dùng cho Sheet trống (một tab mặc định).

## Giới hạn Drive đã đo (2026-10-23)
Connector Google Drive chở file nhị phân dưới dạng base64 trong hội thoại: 2KB khớp checksum; 28KB vượt trần → **~20KB/file ảnh**. Không có MD5.
Connector dùng để **tìm, lấy ID/link, tạo thư mục, ghi file chữ** (`textContent`). Ảnh đi bằng Claude in Chrome tải lên giao diện Drive (Asset Publishing, cách A), người dùng kéo thả, hoặc Drive for Desktop (`ia drive setup --che-do dong-bo`).

## Asset Retrieval (trước khi dựng)
1. `ia assets find <từ khoá> [--loai …]` — tab 02 Source (bộ đệm) + Brand Kit + ảnh đã có trên máy.
2. Chưa có trong Sheet → connector `search_files` trong `01 Ảnh/01 Source thô` (id trong `image-studio.json` → drive.source_id), theo nhóm → tên.
   **Không quét cả Drive.** Thấy file chưa có dòng Source → đăng ký: `ia assets add <file|-> --loai … --nhom "<Nhóm>" --tag "…" --drive-id <id> --quyen …`.
3. Lấy ảnh về máy: file ≤ 20KB (logo nhỏ, icon) → `download_file_content` → `base64 -D` vào `jobs/DS/assets/`. Lớn hơn → nhờ người dùng kéo vào chat / `jobs/DS/input/` (nêu tên + link), hoặc dùng thẳng đường dẫn đồng bộ.
4. Ảnh người dùng gửi thẳng cho một việc → nhắc họ đưa bản gốc vào `01 Source thô/07 Theo việc/<DS>/` (agent tạo sẵn thư mục) để Link source thô có giá trị.
5. Nhiều ảnh gần giống → xem ảnh, đưa 2–4 lựa chọn. Không có ảnh phù hợp → **báo thiếu**. Ảnh người: Tag phải có tên người.

## Asset Publishing (sau khi duyệt — mặc định, không hỏi lại)
`ia export` → `ia check` → `ia publish DS` → làm đúng các bước lệnh in ra:
1. `01 Ảnh/02 Final` (drive.final_id) → thư mục tháng → thư mục `DS-… · tên` → thư mục con `_nguon` (search trước, thiếu mới `create_file` folder). Không chia sẻ, không đổi quyền.
2. File chữ vào `_nguon` bằng `textContent`, `disableConversionToGoogleType: true`.
3. Ảnh/PDF từ `jobs/DS/ban-giao/` vào thư mục việc:
   - **Cách A — Agent tự tải (mặc định khi có Claude in Chrome):** mở link thư mục việc trên drive.google.com (người dùng đã đăng nhập sẵn) → Mới → Tải tệp lên
     → `file_upload` vào ô chọn tệp với các file cần đưa (≤ 10 file mỗi lần, đã thử chạy với file zip vài chục MB) → chờ thanh tải xong.
     Không đăng nhập hộ; trang đòi đăng nhập → nhờ người dùng. Không đổi quyền chia sẻ.
   - **Cách B:** người dùng kéo thả (gửi link thư mục) — khi không có Chrome hoặc cách A lỗi.
4. `search_files parentId = …` (thư mục việc + `_nguon`) → `ia link DS --url <viewUrl thư mục việc> --folder-id <id> --kiem '{"tên": fileSize,…}' [--source-url <link 07 Theo việc/DS hoặc link ảnh Source>]`.
5. `ia sheet push`. Có phiếu TASK → `ia sync DS xuat-thu` (+ push của content-agent) — link Final ghi vào **cả hai** Sheet.

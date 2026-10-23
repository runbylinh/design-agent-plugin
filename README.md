# image-agent — Agent 02 Ảnh

Agent thiết kế ấn phẩm tĩnh theo Brand Kit, chạy trong Claude Code. Cung cấp Brand Guideline một lần; sau đó chỉ cần đưa chữ + ảnh thô (hoặc mã phiếu của Agent Content)
là có thiết kế đúng thương hiệu, tự kiểm, duyệt, xuất file và đưa lên Google Drive.

Hệ thống 3 agent: **Agent 01 Content** (`content-agent`) → **Agent 02 Ảnh** (plugin này) → **Agent 03 Video** (`video-edit`).

## Làm được
| Nhóm | Cụ thể |
|---|---|
| Thiết kế mới | Thumbnail YouTube · carousel nhiều trang · ảnh Facebook/Instagram (cả khi chỉ có chữ) · ảnh quảng cáo + biến thể thử nghiệm · poster workshop/sự kiện/mở bán · ảnh bìa kênh · biểu đồ, case study · đồ hoạ cho video theo Scene ID |
| Đầu vào | Yêu cầu trực tiếp (chữ, ảnh, ý tưởng, ảnh tham khảo) **hoặc** Brief ảnh / Script video đã duyệt của Agent Content (phiếu `TASK-` trong 04 Production) |
| Sửa | Mở lại job cũ, sửa đúng phần được yêu cầu, giữ nguyên phần đã chốt; dựng lại từ ảnh PNG/JPG cũ |
| Tái sử dụng | Đổi kích thước (dàn lại bố cục, không kéo giãn) · nhân bản hàng loạt từ mẫu · thư viện mẫu đã duyệt |
| Kiểm & quản lý | QA trước duyệt + sau xuất · phiên bản V1→V2→V3 · khoá chữ đã duyệt · phát hiện Brief/Script đổi · bàn giao Drive + cập nhật 04 Production |

## Google Drive + Sheet (v0.2.0)
Trong thư mục brand của Content Workspace:
```
Media Assets/
├── <BRAND> | Hệ thống Design ảnh   ← Sheet: 00 Hướng dẫn · 01 Brief & Việc · 02 Source · 03 Recap thiết kế · 04 Tiêu chuẩn
├── 01 Source thô/  (01 Logo & nhận diện · 02 Người · 03 Sản phẩm - Dịch vụ · 04 Bối cảnh · 05 Đồ hoạ & thành phần · 06 Tham khảo · 07 Theo việc)
└── 02 Final/       (00 Mẫu đã duyệt · <YYYY-MM>/<DS · tên>/ + _nguon/)
```
Sheet ghi lại Brief, link ảnh thô, link thành phẩm và toàn bộ quá trình dựng – sửa – duyệt – xuất – bàn giao. Agent đọc/ghi qua connector Google Sheets
(`ia sheet pull` / `ia sheet push`), chỉ ghi ô nó đổi. Cấu trúc ở `templates/tracker.json`; Sheet mới: `ia sheet init-plan`.

## Giới hạn
- Dàn trang từ tài nguyên có sẵn, không vẽ minh hoạ tay. AI tạo ảnh chỉ cho nền/hoạ tiết, không viết chữ.
- Tách nền chạy trên máy (rembg); tóc xoà, vật trong suốt có thể cần che mép hoặc ảnh khác.
- Google Drive qua connector chỉ chở được file ảnh ~20KB (đã đo) → ảnh thành phẩm người dùng kéo vào Drive (Agent tạo thư mục, ghi file nguồn, đối chiếu, lấy link),
  hoặc dùng Google Drive for Desktop (chế độ `dong-bo`).
- Font thương mại cần file; không có thì dùng font gần nhất và báo rõ.
- Không đăng bài, không làm video/ảnh động. Canva: để giai đoạn sau.

## Cài đặt
```
/plugin marketplace add <đường dẫn hoặc repo của plugin>
/plugin install image-agent@image-agent-dev
```
Rồi nói "cài agent ảnh" (skill `setup`): cài môi trường `~/.image-agent` (không cần mật khẩu), tạo studio, học Brand Guideline, nối Drive & Agent Content.

## Skill
| Lệnh | Việc |
|---|---|
| `/image-agent:setup` | cài đặt, Brand Kit, Drive, Agent Content |
| `/image-agent:design` | thiết kế mới (mọi loại, mọi đầu vào) |
| `/image-agent:edit` | sửa thiết kế có sẵn, nguồn đổi |
| `/image-agent:adapt` | đổi kích thước, nhân bản, mẫu |
| `/image-agent:status` | việc đang làm/chờ duyệt/chờ upload, mở lại việc cũ |
Subagent `design-qa` soát thiết kế độc lập (chỉ đọc).

## Cấu trúc
```
bin/ia                 lệnh dòng lệnh (ia help)
engine/                Python: tracker (Sheet), compose (design.json → HTML), render (Playwright → PNG + kiểm tự động), export, cutout, chart, job, content, publish, adapt
templates/layouts/     10 bố cục, mỗi bố cục có biến thể 16:9 / 4:5 / 1:1 / 9:16 (+3:1, 21:9 cho ảnh bìa)
templates/brand-kit/   mẫu Brand Kit
references/            nguyên tắc, điều phối 15 Use Case, design.json, hợp đồng bàn giao v1, Media Assets, QA, quy tắc theo loại ấn phẩm
skills/ agents/        5 skill + design-qa
tests/run.sh           48 tình huống
```
Studio (ngoài plugin): `image-studio.json`, `jobs/DS-YYMMDD-NN/` (manifest, input, assets, v1…, approved), `.tracker/` (bộ đệm Sheet + hàng đợi ghi).
Brand Kit dùng chung với `video-edit` (cùng `brand.json`).

## Kiểm thử
`bash tests/run.sh`

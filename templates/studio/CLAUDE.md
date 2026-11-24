# Studio — Agent 02 Design (design-agent)

Thư mục này là studio của Agent 02 Design. Mọi lệnh chạy bằng `${CLAUDE_PLUGIN_ROOT}/bin/ia` (hoặc `ia` nếu đã có trong PATH).

- `image-studio.json` — Brand Kit, chế độ Drive, workspace Agent Content.
- `jobs/DS-…/` — mỗi việc thiết kế một thư mục: `manifest.json` (lịch sử, duyệt, bàn giao), `input/`, `assets/`, `v1/ v2/ …` (design.json + ảnh dựng), `approved/` (thành phẩm + file nguồn).
- `research/RS-…/` — phiên nghiên cứu mẫu (`/design-agent:research`): `mau/` ảnh mẫu kèm nguồn, `moodboard.png`, `phan-tich.md`, `thu/` bố cục thử.
- `landing/LP-…/` — landing page (`/design-agent:landing`): `brief.md`, `v1/ v2/ …` (index.html, assets, ảnh chụp kiểm tra), `final/`.
- `.tracker/` — bộ đệm Sheet "Hệ thống Design ảnh" + hàng đợi ghi (`ia sheet status`, `ia sheet push`). `_assets.json` — tài nguyên chỉ có trên máy.

Không sửa tay `manifest.json`. Không xoá thư mục phiên bản cũ.
Hỏi "đang có việc gì" → `/design-agent:status`.

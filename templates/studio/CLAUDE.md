# Studio ảnh — Agent 02 (image-agent)

Thư mục này là studio của Agent 02 Ảnh. Mọi lệnh chạy bằng `${CLAUDE_PLUGIN_ROOT}/bin/ia` (hoặc `ia` nếu đã có trong PATH).

- `image-studio.json` — Brand Kit, chế độ Drive, workspace Agent Content.
- `jobs/DS-…/` — mỗi việc thiết kế một thư mục: `manifest.json` (lịch sử, duyệt, bàn giao), `input/`, `assets/`, `v1/ v2/ …` (design.json + ảnh dựng), `approved/` (thành phẩm + file nguồn).
- `_assets.json` — thư viện tài nguyên đã đăng ký.

Không sửa tay `manifest.json`. Không xoá thư mục phiên bản cũ.
Hỏi "đang có việc gì" → `/image-agent:status`.

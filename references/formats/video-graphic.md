# Đồ hoạ cho video — Graphic Pack (D12, D14)

Agent 02 **chỉ dựng đồ hoạ tĩnh** để Agent Video (plugin `video-edit`) đặt vào video. Không cắt dựng, không phụ đề, không làm cảnh quay.

## Khổ
| Dùng | Preset | Ghi chú |
|---|---|---|
| Thẻ phủ lên video dọc | `video_overlay_9x16` | nền trong suốt; tránh nút TikTok/Reels bên phải, phụ đề + caption phía dưới, thanh trên |
| Thẻ video ngang | `video_card_16x9` | tránh dải phụ đề dưới |
| Ảnh full màn hình (cảnh đồ hoạ) | `story_9x16` / `chart_16x9` | có nền |
| Thumbnail / ảnh bìa video | `youtube_thumbnail` | xem thumbnail.md |

Bố cục `the-video` (vùng `card`, `hook`, `list`, `chart`, `stat`, `sub`, `source`, `cta`).

## Từ script → Graphic Asset List (D14)
1. `ia brief TASK-… --job DS` (hoặc `--file script.md`) — chữ đã duyệt theo cảnh, mã băm từng cảnh.
2. `ia asset-list DS` → danh sách gợi ý. Claude **đọc lại script** và sửa danh sách: chỉ giữ cảnh thật sự cần đồ hoạ
   (chữ màn hình Brief yêu cầu, số liệu/sơ đồ/so sánh khó hiểu nếu chỉ nghe, tổng kết ý, CTA cuối). Không thêm đồ hoạ chỉ để "nhiều hiệu ứng".
3. Trình người dùng bảng: `Mã · Scene ID · timecode (nếu có) · loại · nội dung · lý do cần` → **chờ duyệt** rồi mới dựng.
4. Mỗi đồ hoạ = một trang trong design.json với `id` = Scene ID → file `DS-…-SC-03.png`.

## Nhận yêu cầu cụ thể từ Agent Video (D12)
Agent Video / người dùng nêu rõ cần gì ("thẻ CTA cuối 3 giây", "bảng so sánh cảnh 4") → dựng đúng thế, không cần lập danh sách.

## Bàn giao Graphic Pack
`approved/` gồm PNG trong suốt theo Scene ID + `huong-dan-dat.md` (Claude viết): mỗi file — Scene ID, timecode/câu thoại tương ứng,
vị trí đặt (toàn khung / nửa trên), thời lượng gợi ý, hiệu ứng vào/ra gợi ý (nếu Brief có). Không đặt đồ hoạ đè phụ đề.
Script đổi sau khi đã dựng → `ia source-check DS` (D15).

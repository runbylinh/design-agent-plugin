# design.json — bản mô tả thiết kế (nguồn của mọi file ảnh)

HTML và PNG đều **dựng ra từ** design.json. Sửa thiết kế = sửa design.json rồi `ia render`. Không sửa tay index.html.

## Khung
```json
{
  "design_id": "DS-261023-01",
  "brand": "rbl",
  "output_type": "thumbnail | carousel | facebook | anh_don | quang_cao | poster | anh_bia | bieu_do | video_graphic | story",
  "content_id": "CT-2610-015",
  "canvas": {"preset": "youtube_thumbnail"},          // hoặc {"w":1200,"h":628} — xem `ia presets`
  "layout": "chu-trai-chu-the-phai",                    // bố cục mặc định cho mọi trang — xem `ia layouts`
  "bg": {"color": "light"},                             // nền mặc định
  "chrome": {"handle": "@runbylinh", "page_number": true, "swipe": true},   // chỉ carousel
  "export": {"formats": ["png", "pdf"], "max_kb": 500},
  "pages": [ { "id": "p1", "layout": "…", "bg": {…}, "dark": false, "elements": [ … ] } ]
}
```
- Ảnh đơn: một trang. Carousel: mỗi trang một phần tử của `pages`. Đồ hoạ video: **id trang = Scene ID** (`SC-03`) → file `DS-…-SC-03.png`.
- `dark: true` cho trang nền tối (chữ số trang chuyển trắng).

## Nền (`bg`)
| Khoá | Ví dụ | Ghi chú |
|---|---|---|
| `color` | `"paper"`, `"light"`, `"primary"`, `"#FFF7ED"`, `"gradient:primary,highlight,135"` | tên màu trong Brand Kit hoặc mã |
| `image` | `"assets/cua-hang.jpg"` | ảnh tràn khung (ảnh bối cảnh — KHÔNG tách nền) |
| `position` | `"center top"` | vị trí ảnh nền |
| `overlay` | `"dim"`, `"gradient-bottom"`, `"gradient-left"` | lớp tối để chữ đọc được trên ảnh |
| `pattern` | `"dots"` | hoạ tiết nhẹ |
| `transparent` | `true` | PNG trong suốt (đồ hoạ phủ video) |

## Thành phần (`elements`)
Mọi thành phần có `id` (duy nhất trong trang), `type`, `role`. Vị trí: `box` **hoặc** vùng của bố cục theo `slot` (mặc định = `role`).
- `box`: `[x, y, w, h]` — số 0–1 là tỉ lệ khung, số lớn hơn là px. Chỉ dùng `box` khi bố cục không có vùng phù hợp; đổi kích thước sẽ không dàn lại thành phần có `box`.
- `z`: lớp (mặc định 2). Nền trang trí 1, chủ thể 3, chữ 2–4.

| type | Trường riêng | Dùng cho |
|---|---|---|
| `text` | `content` (`**nhấn**`, `\n` xuống dòng) | hook, tiêu đề, mô tả, nhãn, nguồn |
| `list` | `items: []`, `icon` (`check`, `number`, `dot`, tên biểu tượng Lucide) | danh sách ý |
| `button` | `content` | CTA |
| `image` | `src`, `fit` (`cover`/`contain`), `position`, `cutout`, `outline` (`"10 #FFFFFF"`), `shadow`, `rounded` | ảnh người/sản phẩm, ảnh minh hoạ |
| `logo` | `nen`: `sang` / `toi` | logo đúng phiên bản theo nền |
| `icon` | `name` (Lucide — `ia icons find …`) | biểu tượng |
| `shape` | `shape`: `rect`/`circle`/`pill`/`line`/`arrow`, `style.fill`, `style.gradient: ["primary","highlight",135]` | khối màu, đường nối, mũi tên |
| `chart` | `spec` (xem `ia chart`) — **bắt buộc `source`** | biểu đồ, bảng, phễu |
| `html` | `html` | trường hợp đặc biệt bố cục không làm được |

`style` (mọi thành phần chữ): `size` (`xs sm md lg xl xxl mega` hoặc `"64px"`), `weight`, `color`, `font` (`heading`/`body`), `align`, `valign`, `line_height`, `tracking`, `uppercase`, `max_lines`, `min_size`, `mark` (`color`/`box`/`underline`), `mark_color`, `box_text` (nền từng dòng), `stroke` (`"8 #000"`), `shadow`, `bg`, `padding`, `radius`.

## Khoá
| Khoá | Nghĩa | Ai đặt |
|---|---|---|
| `content_locked: true` | không đổi chữ/số/CTA. **Được** xuống dòng (`\n`), tô nhấn (`**…**`), đổi cỡ/màu/vị trí | mặc định cho mọi chữ lấy từ Brief đã duyệt |
| `style_locked: true` | không đổi cách thể hiện (vị trí, cỡ, màu, xử lý ảnh) khi chưa được phép | thành phần người dùng bảo "giữ nguyên" khi sửa (D05) |

Lần dựng đầu tiên, `ia render` ghi mã băm chữ khoá vào manifest. Bản sau đổi chữ khoá → **lỗi chặn**, không duyệt được.
Nguồn đã duyệt lại bản mới → `ia lock DS --reset --xac-nhan "…"`.
`style_locked` không có máy kiểm — Claude phải tự giữ: so design.json mới với bản cũ, thành phần style_locked giữ nguyên `box/slot/style/src`.

## Nhiều hướng thiết kế (thiết kế mới, chưa rõ hướng)
`vN/huong-a/design.json`, `vN/huong-b/design.json` (… tối đa 3) → `ia render DS` dựng tất cả + `so-sanh-huong.png`.
Người dùng chọn → `ia version new DS --tu vN --huong b --note "chọn hướng B, tăng chữ"`.

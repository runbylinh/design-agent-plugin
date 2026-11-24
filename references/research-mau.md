# Nghiên cứu mẫu thiết kế — nguồn, khung phân tích, đóng gói

Mục tiêu: hiểu **vì sao** một mẫu hiệu quả rồi dựng lại cấu trúc đó bằng Brand Kit — không sao chép.

## 1. Nguồn
| Nhóm | Nơi xem | Tìm bằng | Lưu ý |
|---|---|---|---|
| Thư viện thiết kế | Pinterest, Behance, Dribbble | từ khoá tiếng Anh: `instagram carousel design 2026`, `educational carousel`, `youtube thumbnail`, `event poster minimal`, `landing page course` | xu hướng thẩm mỹ; nhiều mẫu concept chưa chạy thật |
| Mẫu template | Canva Templates, Figma Community | lọc theo loại ấn phẩm, sắp xếp mới nhất / phổ biến | xem cách chia hệ thống nhiều trang |
| Quảng cáo đang chạy | Meta Ads Library (connector `ads_library_search` hoặc web), TikTok Creative Center | tên brand cùng ngành, từ khoá ngành, quốc gia VN | mẫu **đang chi tiền** → đã qua thử nghiệm; ghi ngày bắt đầu chạy (chạy lâu = hiệu quả) |
| Fanpage / Instagram ngành | trang đối thủ, brand dẫn đầu ngành, creator cùng chủ đề | bài nhiều tương tác 3 tháng gần nhất | ghi số tương tác công khai nếu thấy |
| Người dùng gửi | link, ảnh chụp, file | — | ưu tiên phân tích kỹ nhất |
| Bối cảnh xu hướng | WebSearch "graphic design trends <năm>", "social media design trends <năm>" | 2–3 bài mới nhất | chỉ làm bối cảnh, mẫu thật vẫn là chính |

Mới nhất = ưu tiên 6 tháng gần đây. Mỗi nguồn 3–6 mẫu là đủ; đa dạng hơn quan trọng hơn nhiều.

## 2. Chụp mẫu (Claude in Chrome)
- Mở ảnh bản lớn (bấm vào pin/ảnh/bài; Facebook: mở trình xem ảnh) → rê chuột ra góc → `computer zoom` đúng vùng thiết kế, **`save_to_disk`, scale 1**
  (scale nhỏ hơn thì file lưu cũng nhỏ) → chép file từ tool-results → `ia research add`.
- Carousel: chụp trang bìa + 2–3 trang giữa + trang cuối, mỗi trang một lần `add` cùng `--url`.
- Landing page: chụp màn đầu máy tính, màn đầu điện thoại (thu cửa sổ ~390px) và các section đáng học.
- Không tải hàng loạt bằng script; không đăng nhập hộ người dùng; trang đòi đăng nhập → nhờ người dùng mở sẵn.
- Ảnh mẫu chỉ để tham khảo nội bộ trong `research/RS/mau/` — không đưa vào thành phẩm, không đẩy lên Drive/GitHub công khai.

## 3. Khung phân tích từng mẫu (ghi ngắn, 5–8 dòng/mẫu)
| Mục | Hỏi gì |
|---|---|
| Bố cục | lưới mấy cột, khối chính ở đâu, tỉ lệ chữ/ảnh/khoảng trắng, căn trái hay giữa |
| Phân cấp | mắt nhìn gì trước–sau, mấy cỡ chữ, tiêu đề dài bao nhiêu chữ |
| Chữ | kiểu font (sans/serif/display), độ đậm, viết hoa hay thường, cách nhấn từ khoá (đổi màu / khung / gạch chân) |
| Màu | nền sáng/tối, mấy màu, màu nhấn dùng ở đâu, độ tương phản |
| Ảnh | ảnh người (tách nền? đen trắng? khung?), ảnh chụp màn hình, minh hoạ, icon — chiếm bao nhiêu khung |
| Thành phần lặp | nhãn trên tiêu đề, số thứ tự, thanh tiến trình, chân trang, logo, handle |
| Mật độ & CTA | bao nhiêu chữ, CTA là gì, nằm đâu |
| Vì sao hiệu quả | 1 câu: điều gì khiến người xem dừng lại / hiểu nhanh |
| Hợp brand? | Hợp / Cần chỉnh (chỉnh gì) / Không hợp (vì sao) — đối chiếu `brand.md` "Không làm" |

### 3b. Landing page
Thứ tự section · hero (nhãn, H1 bao nhiêu chữ, câu phụ, nút, ảnh) · cách đặt bằng chứng (số liệu, feedback, logo) · trình bày Offer/giá/hạn ·
số lần lặp CTA · form (mấy trường) · nhịp nền section (trắng/xen màu) · độ dài trang trên điện thoại · điều khác biệt đáng học.

### Tổng hợp
Mẫu lặp = thấy ở ≥3 mẫu từ ≥2 nguồn. Xếp: **Đang nổi** (nhiều ở mẫu mới / quảng cáo mới chạy) · **Phổ biến** (ở khắp nơi) ·
**Bão hoà** (ai cũng dùng, khó nổi bật). Ghi rõ mẫu số minh hoạ.

## 4. Đề xuất hướng áp dụng
Mỗi hướng: tên ngắn tiếng Việt (vd "Tiêu đề trái + thẻ số") · học từ mẫu số … · dùng cho loại ấn phẩm nào · giữ gì của brand (màu, font, logo) ·
khác gì bố cục đang có (`ia layouts`) · rủi ro (chữ nhiều, cần ảnh chất lượng…). 3–5 hướng, sắp theo mức đáng thử.
Nếu một mẫu đã có bố cục tương đương trong plugin → nói rõ, đề xuất chỉnh thay vì tạo mới.

## 5. Viết bố cục mới (`research/RS/thu/<ten>.json`)
Cùng cấu trúc `templates/layouts/*.json`:
```json
{
  "mo_ta": "Tiêu đề trái, 3 thẻ số xếp dọc — carousel kiến thức",
  "dung_cho": ["carousel", "facebook"],
  "variants": {
    "4:5": {"regions": {
      "kicker": {"box": [0.08, 0.07, 0.6, 0.04], "size": "sm"},
      "hook":   {"box": [0.08, 0.12, 0.84, 0.2], "size": "xl"},
      "sub":    {"box": [0.08, 0.36, 0.84, 0.46], "size": "md"},
      "logo":   {"box": [0.08, 0.9, 0.18, 0.05]}
    }},
    "1:1": {"regions": {"…": "…"}}
  }
}
```
- Toạ độ `box` = tỉ lệ `[x, y, w, h]` 0–1. Tên vùng dùng lại tên quen thuộc (`kicker`, `hook`, `sub`, `subject`, `list`, `cta`, `logo`, `badge`, `icon`, `stat`, `source`)
  để `ia resize` dàn lại được.
- Có biến thể cho mọi tỉ lệ sẽ dùng (carousel 4:5 + 1:1; thumbnail 16:9; story 9:16).
- Thành phần trang trí đặc trưng (khung, vạch, thẻ nền) → đặt trong `design.json` mẫu (shape có `box`), không nhồi vào bố cục.
- `ia layout check` phải ✅ trước khi lưu.

## 6. Đóng gói
| Đầu ra | Ở đâu | Lệnh |
|---|---|---|
| Bố cục mới | `Brand Kit/thanh-phan/layouts/<tên>.json` (ưu tiên hơn bố cục cùng tên của plugin; plugin không cho trùng tên) | `ia layout save … --tu RS` |
| Mẫu thiết kế đã duyệt | `Brand Kit/mau/<tên>.json` + ảnh xem trước | `ia approve` → `ia template save` |
| Quy tắc style | `brand.md` mục "Style đã học" (ghi: học từ RS-…, ngày) | sửa tay, **chỉ khi người dùng đồng ý** |
| Hồ sơ nghiên cứu | `research/RS/` (moodboard, phân tích, nguồn) | `ia research done` |
Bố cục/mẫu nằm trong Brand Kit nên dùng chung cho mọi việc sau của brand đó. Không chép bố cục của brand vào thư mục plugin.

## Không làm
- Không chép nguyên ảnh, minh hoạ, nhân vật, logo, câu chữ, bảng màu nhận diện của bên khác. Chỉ học cấu trúc + nguyên tắc.
- Không dựng hàng loạt trước Duyệt 1. Không lưu bố cục chính thức trước Duyệt 2.
- Không ghi tên đối thủ/handle vào tên bố cục, tên mẫu hay brand.md (ghi trong `phan-tich.md` là đủ).

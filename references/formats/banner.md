# Banner web / email / ảnh bìa khác (`ia job new --loai banner`)

| Khổ (preset) | Kích thước | Lưu ý |
|---|---|---|
| `website_banner` | 1920×600 | trên điện thoại hai bên bị cắt → chữ + nút trong 60% giữa |
| `email_header` | 1200×400 (hiện 600×200) | chữ ≥ 40px ở khổ file; nhiều hộp thư tắt ảnh → nội dung chính vẫn phải có trong chữ email |
| `linkedin_banner` | 1584×396 | avatar che góc trái dưới → nội dung lệch phải |
| `zalo_post` | 1200×900 | ảnh bài viết Zalo OA |
| `tiktok_cover` | 1080×1920 | ảnh bìa video; lưới hồ sơ cắt còn 3:4 giữa → tiêu đề nằm giữa khung |
| `zalo_cover`, `facebook_cover`, `youtube_banner` | xem `formats/anh-bia.md` | |

- Một câu + một nút/hành động; logo nhỏ. Không nhồi thông tin của landing page vào banner.
- Email: xuất JPG ≤ 200KB (`ia export DS --dinh-dang jpg --max-kb 200`).
- Website: xuất thêm bản 9:16/4:5 cho điện thoại bằng `ia resize` nếu trang dùng ảnh riêng cho điện thoại.
- Đặt lên thiết bị để trình duyệt / bán khoá học: `ia mockup <ảnh> --kieu dien-thoai|laptop|sach|the` (xem `qa.md` không áp cho mockup — mockup chỉ là ảnh trình bày).

# QA — hai thời điểm, ba nhóm

Máy kiểm (`qa.json`, `qa-sau-xuat.json`) chỉ là một phần. **Luôn mở ảnh ra xem.** Subagent `design-qa` làm phần nhìn bằng mắt.

## QA lần 1 — trước khi trình duyệt (sau `ia render`)
### A. Đúng Brief
- [ ] Đúng nguồn (bản Brief/script đã khoá; `ia source-check` nếu job từ Agent Content)
- [ ] Đủ nội dung: từng dòng chữ trong Brief đều có trên ảnh, đúng thứ tự ưu tiên
- [ ] Chữ khoá không đổi (máy kiểm), số liệu/Offer/CTA đúng từng ký tự
- [ ] Đúng loại ấn phẩm, khổ, số trang, số phương án
### B. Đúng thiết kế
- [ ] Brand Kit: màu, font, logo đúng phiên bản nền, quy tắc `khong_lam`
- [ ] Dấu tiếng Việt đủ, không vỡ font (ắ, ệ, ờ, ữ…), không chữ rớt một mình cuối dòng ("sách" / "đơn" đứng lẻ), không ngắt dòng giữa cụm từ
- [ ] Phân cấp rõ: nhìn 1 giây biết đọc gì trước
- [ ] Không có gì tràn khung, đè nhau ngoài ý muốn, sát mép
- [ ] Vùng an toàn / vùng bị che của nền tảng (máy kiểm)
- [ ] Tương phản (máy kiểm) — và nhìn lại chữ nhấn
- [ ] Ảnh: không mờ/vỡ, viền tách nền sạch (xem `*-kiem-vien.png`), chủ thể không bị cắt chỗ quan trọng (đầu, tay, sản phẩm)
- [ ] `xem-dien-thoai.png`: đọc được ở cỡ điện thoại
- [ ] Carousel: `xem-nhanh.png` — cùng hệ thống, trang 1 nổi bật, mạch đọc liền
### C. Biểu đồ
- [ ] Số khớp nguồn, đơn vị, nhãn, có dòng nguồn, trục từ 0

## QA lần 2 — sau khi xuất (`ia export` tự chạy `ia check`)
- [ ] Mở lại từng file: đúng kích thước, đúng định dạng, không bị cắt/vỡ khi nén (máy so với bản dựng)
- [ ] Trong suốt khi yêu cầu (đồ hoạ video) — máy kiểm
- [ ] Font không bị thay (máy kiểm khi dựng lại bản duyệt)
- [ ] Dung lượng trong giới hạn
- [ ] Đủ bộ: mọi trang/Scene ID, PDF đủ trang, design.json + source.html + manifest.json
- [ ] Tên file khớp DS ID / Scene ID
- [ ] Mở `approved/xem-dien-thoai/` xem bằng mắt lần cuối

Lỗi chặn → sửa (phiên bản mới) trước khi trình duyệt / bàn giao. Người dùng muốn chấp nhận lỗi → ghi rõ trong lời xác nhận, dùng `--chap-nhan-loi`.
Tối đa 2 vòng tự sửa sau góp ý QA của chính mình; vẫn lỗi → trình người dùng kèm vấn đề còn lại.

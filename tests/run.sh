#!/usr/bin/env bash
# Kiểm thử Agent 02 Ảnh: studio, brand, dựng, khoá chữ, duyệt, xuất, QA sau xuất, trong suốt, đổi khổ, nhân bản, mẫu,
# Brief/script, Graphic Asset List, nguồn đổi, bàn giao Drive, tìm việc cũ. Chạy: bash tests/run.sh
# (Không tách nền — tránh tải model; tách nền thử bằng tay: ia cutout.)
set -u
PLUGIN="$(cd "$(dirname "$0")/.." && pwd)"
IA="$PLUGIN/bin/ia"
PY="${IMAGE_AGENT_HOME:-$HOME/.image-agent}/env/bin/python"
T="$PLUGIN/tests/.tmp"
rm -rf "$T"; mkdir -p "$T"
PASS=0; FAIL=0
ok()   { PASS=$((PASS+1)); echo "  ✅ $1"; }
bad()  { FAIL=$((FAIL+1)); echo "  ❌ $1"; }
expect_code() { local want=$1 name=$2; shift 2; "$@" >"$T/out.txt" 2>&1; local got=$?; [ "$got" = "$want" ] && ok "$name" || { bad "$name (mã $got, cần $want)"; tail -5 "$T/out.txt"; }; }
expect_out()  { local pat=$1 name=$2; shift 2; "$@" >"$T/out.txt" 2>&1; grep -q -- "$pat" "$T/out.txt" && ok "$name" || { bad "$name (không thấy '$pat')"; tail -5 "$T/out.txt"; }; }

echo "■ Studio & Brand Kit"
mkdir -p "$T/kit/logo"
cp "$PLUGIN/templates/brand-kit/brand.json" "$T/kit/brand.json"
for i in $(seq 1 30); do echo "Tinh thần thương hiệu: rõ ràng, gần gũi, chuyên môn." ; done > "$T/kit/brand.md"
"$PY" - "$T" <<'EOF'
import sys
from PIL import Image, ImageDraw
t = sys.argv[1]
for name, col in (("logo-mau", (139, 92, 246)), ("logo-trang", (255, 255, 255))):
    im = Image.new("RGBA", (400, 120), (0, 0, 0, 0)); ImageDraw.Draw(im).rounded_rectangle([0, 0, 120, 120], 28, fill=col)
    im.save(f"{t}/kit/logo/{name}.png")
im = Image.new("RGB", (1200, 800), (200, 190, 170)); ImageDraw.Draw(im).ellipse([400, 150, 800, 650], fill=(90, 60, 200)); im.save(f"{t}/anh.jpg")
EOF
expect_code 0 "tạo studio nối Brand Kit" "$IA" studio init "$T/st" --brand-kit "$T/kit" --brand demo
cd "$T/st"
expect_out "đủ để dựng ảnh" "brand check đạt" "$IA" brand check
expect_out "youtube_thumbnail" "presets" "$IA" presets
expect_out "chu-trai-chu-the-phai" "layouts" "$IA" layouts

echo "■ Thiết kế mới → dựng → khoá chữ → duyệt → xuất"
D1=$("$IA" job new --loai thumbnail --ten "Thử thumbnail" | tail -1)
cp "$T/anh.jpg" "jobs/$D1/assets/anh.jpg"
cat > "jobs/$D1/v1/design.json" <<'EOF'
{"brand":"demo","canvas":{"preset":"youtube_thumbnail"},"layout":"chu-trai-chu-the-phai","bg":{"color":"paper"},
 "pages":[{"id":"p1","elements":[
  {"id":"h","type":"text","role":"hook","content":"Bí quyết\n**x3 doanh số**","content_locked":true,"style":{"mark_color":"primary"}},
  {"id":"s","type":"image","role":"subject","src":"assets/anh.jpg","fit":"cover","rounded":true},
  {"id":"l","type":"logo","role":"logo"}]}]}
EOF
expect_code 0 "dựng v1 không lỗi" "$IA" render "$D1"
[ -f "jobs/$D1/v1/out/p1.png" ] && [ -f "jobs/$D1/v1/xem-dien-thoai.png" ] && ok "có ảnh + bản xem điện thoại" || bad "thiếu ảnh dựng"
"$PY" -c "from PIL import Image; im=Image.open('jobs/$D1/v1/out/p1.png'); assert im.size==(1280,720)" && ok "đúng 1280×720" || bad "sai kích thước"
"$IA" version new "$D1" --note "đổi chữ" >/dev/null
sed -i.bak 's/x3 doanh số/x5 doanh số/' "jobs/$D1/v2/design.json"
expect_out "đã bị đổi chữ" "chặn đổi chữ khoá" "$IA" render "$D1"
expect_code 2 "không duyệt được bản có lỗi chặn" "$IA" approve "$D1" --v 2 --xac-nhan "ok"
"$IA" version new "$D1" --tu v1 --note "xuống dòng khác" >/dev/null
sed -i.bak 's/Bí quyết\\n\*\*x3 doanh số\*\*/Bí quyết **x3**\\ndoanh số/' "jobs/$D1/v3/design.json"
expect_code 0 "xuống dòng + đổi nhấn vẫn hợp lệ" "$IA" render "$D1"
expect_code 1 "approve thiếu lời xác nhận bị từ chối" "$IA" approve "$D1" --v 3
expect_code 0 "duyệt v3" "$IA" approve "$D1" --v 3 --xac-nhan "Duyệt bản 3"
expect_out "đạt" "xuất + QA sau xuất" "$IA" export "$D1" --dinh-dang png,jpg --max-kb 300
[ -f "jobs/$D1/approved/design.json" ] && [ -f "jobs/$D1/approved/source.html" ] && ok "có file nguồn trong approved/" || bad "thiếu file nguồn"

echo "■ Tương phản & vùng bị che"
D2=$("$IA" job new --loai thumbnail --ten "Tương phản kém" | tail -1)
cat > "jobs/$D2/v1/design.json" <<'EOF'
{"brand":"demo","canvas":{"preset":"youtube_thumbnail"},"bg":{"color":"#FFFFFF"},
 "pages":[{"id":"p1","elements":[
  {"id":"mo","type":"text","content":"Chữ quá nhạt","box":[0.05,0.1,0.6,0.3],"style":{"color":"#EEEEEE","size":"xl"}},
  {"id":"goc","type":"text","content":"Đè thời lượng","box":[0.82,0.85,0.16,0.1],"style":{"color":"#000000","size":"sm"}}]}]}
EOF
"$IA" render "$D2" > "$T/out.txt" 2>&1
grep -q "tương phản" "$T/out.txt" && ok "bắt tương phản thấp" || bad "không bắt tương phản"
grep -q "thời lượng video" "$T/out.txt" && ok "bắt chữ đè vùng thời lượng YouTube" || bad "không bắt vùng bị che"

echo "■ Carousel nhiều hướng + chrome + biểu đồ thiếu nguồn"
D3=$("$IA" job new --loai carousel --ten "Thử carousel" | tail -1)
rm "jobs/$D3/v1/design.json"; mkdir -p "jobs/$D3/v1/huong-a" "jobs/$D3/v1/huong-b"
cat > "jobs/$D3/v1/huong-a/design.json" <<'EOF'
{"brand":"demo","canvas":{"preset":"carousel_4x5"},"chrome":{"handle":"@demo"},"bg":{"color":"light"},
 "pages":[{"id":"p1","layout":"tieu-de-giua","elements":[{"id":"h","type":"text","role":"hook","content":"Năm sai lầm","content_locked":true}]},
          {"id":"p2","layout":"danh-sach","elements":[{"id":"t","type":"text","role":"hook","content":"Danh sách"},{"id":"l","type":"list","role":"list","items":["Một","Hai","Ba"]}]},
          {"id":"p3","layout":"so-lieu","elements":[{"id":"c","type":"chart","role":"chart","spec":{"kind":"bar","labels":["A","B"],"series":[{"name":"x","values":[3,5]}]}}]}]}
EOF
sed 's/"layout":"tieu-de-giua"/"layout":"anh-nen-tran"/' "jobs/$D3/v1/huong-a/design.json" > "jobs/$D3/v1/huong-b/design.json"
"$IA" render "$D3" > "$T/out.txt" 2>&1
grep -q "chưa ghi nguồn" "$T/out.txt" && ok "chặn biểu đồ thiếu nguồn" || bad "không chặn biểu đồ thiếu nguồn"
[ -f "jobs/$D3/v1/so-sanh-huong.png" ] && ok "dựng 2 hướng + ảnh so sánh" || bad "thiếu so-sanh-huong.png"
"$IA" version new "$D3" --tu v1 --huong b --note "chọn B" >/dev/null && [ -f "jobs/$D3/v2/design.json" ] && ok "tạo v2 từ hướng B" || bad "không tạo được v2 từ hướng"

echo "■ Đồ hoạ video trong suốt + script + Graphic Asset List + nguồn đổi"
cat > "$T/script.md" <<'EOF'
[Cảnh 1] SC-01 lời: Mở đầu | chữ màn hình: Nhiều view ≠ ra đơn
[Cảnh 2] SC-02 lời: Kể chuyện | hình: B-roll
[Cảnh 3] SC-03 lời: Phễu | hình: sơ đồ phễu 100.000 view → 36 đơn
EOF
D4=$("$IA" job new --loai video_graphic --ten "Thử đồ hoạ video" | tail -1)
expect_out '"SC-03"' "tách script theo Scene ID" "$IA" brief --file "$T/script.md" --job "$D4"
expect_out "G02 · SC-03" "Graphic Asset List chọn đúng cảnh cần đồ hoạ" "$IA" asset-list "$D4"
cat > "jobs/$D4/v1/design.json" <<'EOF'
{"brand":"demo","canvas":{"preset":"video_overlay_9x16"},"bg":{"transparent":true},"layout":"the-video",
 "pages":[{"id":"SC-03","elements":[{"id":"card","type":"shape","role":"card","style":{"fill":"#FFFFFF"},"z":1},
   {"id":"t","type":"text","role":"hook","content":"Phễu"},
   {"id":"f","type":"chart","role":"chart","spec":{"kind":"funnel","labels":["View","Đơn"],"series":[{"name":"","values":[100000,36]}],"source":"script SC-03"}}]}]}
EOF
"$IA" render "$D4" >/dev/null 2>&1; "$IA" approve "$D4" --v 1 --xac-nhan "ok" >/dev/null
expect_code 0 "xuất PNG trong suốt đạt QA" "$IA" export "$D4"
[ -f "jobs/$D4/approved/$D4-SC-03.png" ] && ok "tên file theo Scene ID" || bad "sai tên file Scene ID"
sed -i.bak 's/36 đơn/40 đơn/' "$T/script.md"
expect_code 3 "phát hiện script đổi (mã 3)" "$IA" source-check "$D4"
grep -q '"SC-03"' "$T/out.txt" || true
"$IA" source-check "$D4" | grep -q "Sửa: SC-03" && ok "chỉ đúng cảnh đổi SC-03" || bad "không chỉ ra cảnh đổi"

echo "■ Đổi khổ, mẫu, nhân bản"
expect_out "Facebook/Instagram 4:5" "resize sang 4:5" "$IA" resize "$D1" --preset facebook_4x5
D5=$(ls jobs | sort | tail -1)
expect_code 0 "dựng bản resize" "$IA" render "$D5"
"$PY" -c "from PIL import Image; assert Image.open('jobs/$D5/v1/out/p1.png').size==(1080,1350)" && ok "bản resize 1080×1350" || bad "resize sai khổ"
expect_out "Đã lưu mẫu" "lưu mẫu từ bản duyệt" "$IA" template save "$D1" --ten mau-thumb --cho-doi h
cat > "$T/rows.json" <<'EOF'
[{"ten":"Chủ đề 1","noi_dung":{"h":"Chủ đề **một**"}},{"ten":"Chủ đề 2","noi_dung":{"h":"Chủ đề **hai**"}}]
EOF
expect_out "Đã tạo 2 job" "nhân bản 2 job từ mẫu" "$IA" batch mau-thumb --data "$T/rows.json"
cat > "$T/rows-sai.json" <<'EOF'
[{"ten":"Sai","noi_dung":{"h":"x"},"anh":{"s":"assets/khac.png"}}]
EOF
expect_code 1 "mẫu chặn đổi thành phần không cho đổi" "$IA" batch mau-thumb --data "$T/rows-sai.json"

echo "■ Bàn giao Drive"
expect_out "kéo" "publish thủ công hướng dẫn kéo file" "$IA" publish "$D1"
expect_code 2 "link thiếu file bị chặn" "$IA" link "$D1" --url "https://drive.google.com/drive/folders/x" --kiem '{}'
KIEM=$("$PY" -c "import json,os;d='jobs/$D1/ban-giao';print(json.dumps({f:os.path.getsize(os.path.join(d,f)) for f in os.listdir(d)}))")
expect_code 0 "link đủ file + đúng dung lượng" "$IA" link "$D1" --url "https://drive.google.com/drive/folders/x" --kiem "$KIEM"
expect_out "Đã bàn giao" "trạng thái đã bàn giao" "$IA" status --tat-ca
expect_out "$D1" "tìm job cũ theo tên" "$IA" job find thumbnail

echo "■ Sheet Hệ thống Design ảnh (hàng đợi ghi qua connector)"
expect_code 0 "nối Sheet" "$IA" sheet connect --url "https://docs.google.com/spreadsheets/d/1AbCdEfGhIjKlMnOpQrStUvWxYz0123456789abcdefg/edit" --media-assets "https://drive.google.com/drive/folders/1FakeMediaAssetsFolderId0000000000" --final-id FINAL123456789012345
expect_code 0 "kế hoạch tạo cấu trúc" "$IA" sheet init-plan
"$PY" -c "import json;p=json.load(open('.tracker/init-plan.json'));assert sum('addSheet' in r for r in p['update_spreadsheet'])==4;assert '(' not in json.dumps(p['update_spreadsheet']).split('fields')[1][:5]" && ok "init-plan đủ 4 tab, field mask không dùng ngoặc" || bad "init-plan sai"
cat > "$T/viec.json" <<'EOF'
{"range":"'01 Brief & Việc'!A3:Z","values":[["DS ID","Tháng","Brand","Nguồn","CT ID","TASK ID","Loại ấn phẩm","Kênh","Khổ","Brief ảnh","Chữ trên ảnh (đã duyệt)","Tiêu chuẩn áp dụng","Yêu cầu riêng","Hạn","Trạng thái","Bản đang làm","Bản duyệt","Người duyệt","Ngày duyệt","Link source thô","Link final","Ghi chú"],["DS-990101-01","2026-10","demo","Trực tiếp","","","Thumbnail","","","","","","","","Mới","v1","","","","","","ghi chú người dùng"]]}
EOF
echo '{"values":[["AS ID","Nhóm","Tên","Tag","Link Drive","Drive File ID","Quyền dùng","Trạng thái","Người cung cấp","Ngày thêm","Dùng trong DS","Ghi chú"],["AS-007","Người","Diễn giả chỉ tay","dien gia, chan dung","https://drive.google.com/file/d/x","x","Nội bộ","Đã duyệt","","","",""]]}' > "$T/source.json"
echo '{"values":[["DS ID","Phiên bản","Ngày","Bước","Đã làm / đổi gì","Góp ý người dùng","QA máy","QA design-qa","Quyết định","Ghi chú"]]}' > "$T/recap.json"
expect_out "1 dòng" "pull tab 01" "$IA" sheet pull Viec --file "$T/viec.json"
"$IA" sheet pull Source --file "$T/source.json" >/dev/null; "$IA" sheet pull Recap --file "$T/recap.json" >/dev/null
D6=$("$IA" job new --loai facebook --ten "Thử Sheet" | tail -1)
"$PY" - "$D6" <<'EOF' && ok "job mới → dòng 5 tab 01, có Loại/Trạng thái" || bad "job mới không vào hàng đợi đúng"
import json, sys
ob = json.load(open(".tracker/outbox.json"))["ops"]
op = [o for o in ob if o["tab"] == "Viec" and o["values"].get("DS ID") == sys.argv[1]][0]
assert op["row"] == 5, op["row"]
assert op["values"]["Loại ấn phẩm"] == "Ảnh Facebook" and op["values"]["Trạng thái"] == "Mới"
EOF
cat > "jobs/$D6/v1/design.json" <<'EOF'
{"brand":"demo","canvas":{"preset":"facebook_4x5"},"layout":"tieu-de-giua","bg":{"color":"light"},
 "pages":[{"id":"p1","elements":[{"id":"h","type":"text","role":"hook","content":"Chỉ có chữ","content_locked":true}]}]}
EOF
"$IA" render "$D6" >/dev/null 2>&1
"$PY" -c "
import json;ob=json.load(open('.tracker/outbox.json'))['ops']
r=[o for o in ob if o['tab']=='Recap'];assert r and r[0]['row']==4 and r[0]['values']['Bước']=='Dựng', r
v=[o for o in ob if o['tab']=='Viec' and o['row']==5][0]['values'];assert v['Trạng thái']=='Chờ duyệt', v" && ok "dựng → Recap dòng 4 + trạng thái Chờ duyệt (gộp cùng lệnh)" || bad "recap/trạng thái sai"
"$IA" approve "$D6" --v 1 --xac-nhan "ok duyệt" >/dev/null
"$IA" sheet set DS-990101-01 "Trạng thái=Đang làm" >/dev/null
"$IA" sheet push > "$T/push.txt" 2>&1
grep -q "'01 Brief & Việc'!O4:P4\|'01 Brief & Việc'!O4:O4" "$T/push.txt" && ok "sửa dòng có sẵn chỉ ghi đúng ô (O4)" || { bad "push ghi sai vùng dòng có sẵn"; grep -n "O4\|A4" "$T/push.txt" | head; }
grep -q "V4" "$T/push.txt" && bad "ghi đè cột Ghi chú của người dùng" || ok "không đụng ô người dùng tự ghi"
"$PY" -c "import json,re;t=open('$T/push.txt').read();p=json.loads(t[:t.index('\nClaude')]);assert len(p['calls'])>=3" && ok "push in lệnh update_values" || bad "push không in được lệnh"
N=$("$PY" -c "import json,re;t=open('$T/push.txt').read();print(len(json.loads(t[:t.index('\nClaude')])['calls']))")
"$IA" sheet push --xong "$N" >/dev/null
"$PY" -c "import json;assert json.load(open('.tracker/outbox.json'))['ops']==[]" && ok "push --xong dọn hàng đợi" || bad "hàng đợi chưa dọn"
"$IA" assets add "$T/anh.jpg" --loai anh --tag "dien gia, san khau" --ten "Diễn giả sân khấu" --quyen noi-bo >/dev/null
"$PY" -c "
import json;ob=json.load(open('.tracker/outbox.json'))['ops'];o=[x for x in ob if x['tab']=='Source'][0]
assert o['values']['AS ID']=='AS-008' and o['row']==5 and o['values']['Quyền dùng']=='Nội bộ', o" && ok "thêm ảnh thô → 02 Source, AS ID nối tiếp Sheet (AS-008)" || bad "Source sai"
expect_out "AS-007" "tìm ảnh từ tab 02 Source" "$IA" assets find dien gia chi tay

echo
echo "Kết quả: $PASS đạt · $FAIL lỗi"
[ "$FAIL" = 0 ]

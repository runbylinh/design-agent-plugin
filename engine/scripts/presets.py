"""Kích thước chuẩn và vùng an toàn theo nền tảng. Toạ độ vùng = tỉ lệ [x, y, w, h] của khung.

safe   : vùng chữ/logo/CTA phải nằm trong
avoid  : các vùng bị giao diện nền tảng che (thời lượng YouTube, nút TikTok, avatar Facebook…)
"""

PRESETS = {
    "youtube_thumbnail": {"w": 1280, "h": 720, "ten": "Thumbnail YouTube 16:9",
                          "safe": [0.04, 0.06, 0.92, 0.88], "avoid": {"thời lượng video": [0.80, 0.82, 0.20, 0.18]}},
    "facebook_4x5": {"w": 1080, "h": 1350, "ten": "Facebook/Instagram 4:5", "safe": [0.06, 0.05, 0.88, 0.90]},
    "facebook_1x1": {"w": 1080, "h": 1080, "ten": "Facebook/Instagram 1:1", "safe": [0.06, 0.06, 0.88, 0.88]},
    "carousel_4x5": {"w": 1080, "h": 1350, "ten": "Carousel 4:5", "safe": [0.07, 0.06, 0.86, 0.88]},
    "carousel_1x1": {"w": 1080, "h": 1080, "ten": "Carousel 1:1", "safe": [0.07, 0.07, 0.86, 0.86]},
    "story_9x16": {"w": 1080, "h": 1920, "ten": "Story / Reels 9:16 (ảnh)",
                   "safe": [0.06, 0.14, 0.88, 0.66], "avoid": {"thanh trên story": [0, 0, 1, 0.14], "ô trả lời/CTA": [0, 0.80, 1, 0.20]}},
    "meta_ads_4x5": {"w": 1080, "h": 1350, "ten": "Quảng cáo Meta feed 4:5", "safe": [0.06, 0.05, 0.88, 0.90]},
    "meta_ads_9x16": {"w": 1080, "h": 1920, "ten": "Quảng cáo Meta story/reels 9:16",
                      "safe": [0.06, 0.14, 0.88, 0.62], "avoid": {"trên 14%": [0, 0, 1, 0.14], "dưới 20%": [0, 0.80, 1, 0.20]}},
    "facebook_cover": {"w": 1640, "h": 624, "ten": "Ảnh bìa Facebook trang",
                       "safe": [0.14, 0.12, 0.72, 0.62], "avoid": {"avatar (máy tính)": [0, 0.60, 0.22, 0.40]}},
    "youtube_banner": {"w": 2560, "h": 1440, "ten": "Ảnh bìa kênh YouTube",
                       "safe": [0.198, 0.353, 0.604, 0.294]},
    "zalo_cover": {"w": 1500, "h": 500, "ten": "Ảnh bìa Zalo OA", "safe": [0.10, 0.12, 0.80, 0.70]},
    "poster_4x5": {"w": 1080, "h": 1350, "ten": "Poster sự kiện (mạng xã hội)", "safe": [0.06, 0.05, 0.88, 0.90]},
    "poster_a4": {"w": 1240, "h": 1754, "ten": "Poster A4 (in, 150dpi)", "safe": [0.06, 0.05, 0.88, 0.90]},
    "linkedin_1x1": {"w": 1200, "h": 1200, "ten": "LinkedIn 1:1", "safe": [0.06, 0.06, 0.88, 0.88]},
    "video_overlay_9x16": {"w": 1080, "h": 1920, "ten": "Đồ hoạ phủ video dọc (PNG trong suốt)",
                           "safe": [0.06, 0.12, 0.76, 0.52],
                           "avoid": {"nút TikTok/Reels bên phải": [0.84, 0.35, 0.16, 0.50], "phụ đề + caption": [0, 0.66, 1, 0.34],
                                     "thanh trên": [0, 0, 1, 0.10]}},
    "video_card_16x9": {"w": 1920, "h": 1080, "ten": "Thẻ đồ hoạ video ngang", "safe": [0.05, 0.08, 0.90, 0.76],
                        "avoid": {"phụ đề": [0, 0.84, 1, 0.16]}},
    "chart_16x9": {"w": 1600, "h": 900, "ten": "Biểu đồ ngang", "safe": [0.05, 0.06, 0.90, 0.88]},
}

TYPE_DEFAULT = {
    "thumbnail": "youtube_thumbnail", "carousel": "carousel_4x5", "facebook": "facebook_4x5", "anh_don": "facebook_4x5",
    "quang_cao": "meta_ads_4x5", "poster": "poster_4x5", "anh_bia": "facebook_cover", "bieu_do": "chart_16x9",
    "video_graphic": "video_overlay_9x16", "story": "story_9x16",
}


def ratio_key(w, h):
    r = w / h
    cands = {"16:9": 16 / 9, "4:5": 4 / 5, "1:1": 1.0, "9:16": 9 / 16, "3:1": 3.0, "21:9": 21 / 9, "3:4": 3 / 4}
    return min(cands, key=lambda k: abs(cands[k] - r))


def get(name):
    if name not in PRESETS:
        raise KeyError(name)
    return PRESETS[name]


def table():
    rows = [f"  {k:20s} {v['w']}×{v['h']}  {v['ten']}" for k, v in PRESETS.items()]
    return "Khổ chuẩn (dùng trong design.json → canvas.preset):\n" + "\n".join(rows)

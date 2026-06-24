"""
生成应用统一图标：.ico (Windows) + .svg (Web favicon)
设计：深蓝底色 + 白色文档 + 金色横线 + 红色印章
"""
from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "frontend", "build")
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "frontend", "public")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def draw_icon(size: int) -> Image.Image:
    """绘制指定尺寸的应用图标"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    s = size  # 缩写

    # ── 1. 圆角矩形背景（深蓝渐变用纯色模拟）──
    radius = s // 6
    # 主背景 #1a56db
    draw.rounded_rectangle([0, 0, s-1, s-1], radius=radius, fill=(26, 86, 219, 255))
    # 内部稍亮区域营造渐变感
    margin = s // 16
    inner_radius = radius - margin
    draw.rounded_rectangle(
        [margin, margin, s-1-margin, s-1-margin],
        radius=inner_radius, fill=(37, 99, 235, 255)
    )

    # ─�─ 2. 白色文档形状 ──
    doc_margin = s // 5
    doc_w = s - 2 * doc_margin
    doc_h = int(doc_w * 1.3)
    doc_x = doc_margin
    doc_y = (s - doc_h) // 2

    # 文档主体（圆角矩形）
    doc_radius = s // 24
    draw.rounded_rectangle(
        [doc_x, doc_y, doc_x + doc_w, doc_y + doc_h],
        radius=doc_radius, fill=(255, 255, 255, 240)
    )

    # 折角效果（右上角三角形切角）
    fold = doc_w // 4
    draw.polygon([
        (doc_x + doc_w - fold, doc_y),
        (doc_x + doc_w, doc_y + fold),
        (doc_x + doc_w, doc_y),
    ], fill=(200, 215, 240, 255))

    # ── 3. 文档上的横线（模拟文字行）──
    line_color = (30, 64, 175, 180)
    line_x_start = doc_x + doc_w // 6
    line_x_end = doc_x + doc_w - doc_w // 6
    line_y_start = doc_y + fold + doc_h // 8
    line_gap = doc_h // 8
    line_thickness = max(1, s // 64)

    for i in range(4):
        ly = line_y_start + i * line_gap
        # 最后一行短一些
        end = line_x_end - (doc_w // 5 if i == 3 else 0)
        draw.rounded_rectangle(
            [line_x_start, ly, end, ly + line_thickness],
            radius=line_thickness, fill=line_color
        )

    # ── 4. 红色印章（右下角圆形）──
    seal_r = s // 8
    seal_cx = doc_x + doc_w - seal_r // 2
    seal_cy = doc_y + doc_h - seal_r // 2
    # 外圈
    draw.ellipse(
        [seal_cx - seal_r, seal_cy - seal_r, seal_cx + seal_r, seal_cy + seal_r],
        fill=(220, 38, 38, 200)
    )
    # 内圈（留白）
    inner_r = int(seal_r * 0.7)
    draw.ellipse(
        [seal_cx - inner_r, seal_cy - inner_r, seal_cx + inner_r, seal_cy + inner_r],
        fill=(255, 255, 255, 0)
    )

    # 印章内"文"字（尝试用系统字体，没有则画十字）
    try:
        # 尝试 Windows 中文字体
        font_paths = [
            "C:/Windows/Fonts/simhei.ttf",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simsun.ttc",
        ]
        font = None
        for fp in font_paths:
            if os.path.exists(fp):
                font = ImageFont.truetype(fp, int(inner_r * 1.2))
                break
        if font:
            bbox = draw.textbbox((0, 0), "文", font=font)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
            tx = seal_cx - tw // 2
            ty = seal_cy - th // 2 - 1
            draw.text((tx, ty), "文", fill=(220, 38, 38, 220), font=font)
    except Exception:
        pass

    return img


# 生成多尺寸 ICO（主图256 + 追加小图，sizes顺序必须匹配）
sizes = [16, 32, 48, 64, 128, 256]
images = [draw_icon(s) for s in sizes]

ico_path = os.path.join(OUTPUT_DIR, "icon.ico")
# 主图 = 256x256 (images[-1])，追加其余小图
main_img = images[-1]
small_imgs = images[:-1]
main_img.save(
    ico_path, format="ICO",
    sizes=[(256, 256)] + [(s, s) for s in sizes[:-1]],
    append_images=small_imgs,
)
print(f"✓ ICO 已生成: {ico_path}")

# 生成 256x256 PNG（electron-builder 也支持 png）
png_path = os.path.join(OUTPUT_DIR, "icon.png")
images[-1].save(png_path, format="PNG")
print(f"✓ PNG 已生成: {png_path}")

# 生成 SVG favicon（用于 web 和 Electron 窗口）
svg_content = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#2563eb"/>
      <stop offset="100%" stop-color="#1a56db"/>
    </linearGradient>
  </defs>
  <rect width="256" height="256" rx="42" fill="url(#bg)"/>
  <g transform="translate(56,28)">
    <path d="M0,0 L105,0 L144,39 L144,180 Q144,192 132,192 L12,192 Q0,192 0,180 Z" fill="white" fill-opacity="0.94"/>
    <path d="M105,0 L105,39 L144,39 Z" fill="#c8d7f0"/>
    <rect x="24" y="64" width="96" height="5" rx="2.5" fill="#1e40af" fill-opacity="0.6"/>
    <rect x="24" y="84" width="96" height="5" rx="2.5" fill="#1e40af" fill-opacity="0.6"/>
    <rect x="24" y="104" width="96" height="5" rx="2.5" fill="#1e40af" fill-opacity="0.6"/>
    <rect x="24" y="124" width="64" height="5" rx="2.5" fill="#1e40af" fill-opacity="0.6"/>
    <circle cx="120" cy="155" r="26" fill="#dc2626" fill-opacity="0.78"/>
    <text x="120" y="163" text-anchor="middle" font-family="sans-serif" font-size="24" font-weight="bold" fill="#dc2626" fill-opacity="0.9">文</text>
  </g>
</svg>'''

svg_path = os.path.join(PUBLIC_DIR, "favicon.svg")
with open(svg_path, "w", encoding="utf-8") as f:
    f.write(svg_content)
print(f"✓ SVG favicon 已生成: {svg_path}")

# 同步到 dist
import shutil
dist_svg = os.path.join(os.path.dirname(__file__), "frontend", "dist", "favicon.svg")
if os.path.exists(os.path.dirname(dist_svg)):
    shutil.copy2(svg_path, dist_svg)
    print(f"✓ SVG 已同步到 dist")

print("\n图标生成完成！")

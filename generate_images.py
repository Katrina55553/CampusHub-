#!/usr/bin/env python
"""为每家店铺生成带名称的彩色占位图"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from PIL import Image, ImageDraw, ImageFont
from food.models import Shop

# 每家店铺的配色方案（背景色, 文字色）
PALETTES = [
    ((255, 107, 53),  (255, 255, 255)),  # 暖橘
    ((255, 179, 71),  (255, 255, 255)),  # 琥珀
    ((76, 175, 80),   (255, 255, 255)),  # 绿色
    ((33, 150, 243),  (255, 255, 255)),  # 蓝色
    ((156, 39, 176),  (255, 255, 255)),  # 紫色
    ((244, 67, 54),   (255, 255, 255)),  # 红色
    ((0, 188, 212),   (255, 255, 255)),  # 青色
    ((255, 152, 0),   (255, 255, 255)),  # 橙色
]

# 食物 emoji 作为装饰
FOOD_ICONS = ["🍜", "🧋", "🍗", "🍲", "🍰", "🍝", "🧁", "🍕"]

shops = Shop.objects.all()
os.makedirs('media/shops', exist_ok=True)

# 尝试加载中文字体
font_paths = [
    "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",     # 黑体
    "C:/Windows/Fonts/simsun.ttc",     # 宋体
]
font_large = None
font_small = None
for fp in font_paths:
    if os.path.exists(fp):
        font_large = ImageFont.truetype(fp, 48)
        font_small = ImageFont.truetype(fp, 24)
        break

if font_large is None:
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

for i, shop in enumerate(shops):
    bg_color, text_color = PALETTES[i % len(PALETTES)]

    # 创建 400x300 图片
    img = Image.new('RGB', (400, 300), bg_color)
    draw = ImageDraw.Draw(img)

    # 绘制装饰圆形（右上角）
    draw.ellipse([280, -60, 460, 120], fill=(min(bg_color[0]+30, 255), min(bg_color[1]+30, 255), min(bg_color[2]+30, 255)))

    # 绘制装饰圆形（左下角）
    draw.ellipse([-80, 180, 120, 380], fill=(max(bg_color[0]-20, 0), max(bg_color[1]-20, 0), max(bg_color[2]-20, 0)))

    # 绘制装饰星形
    draw.text((175, 80), "★", font=font_large, fill=text_color)

    # 绘制店铺名称（居中）
    name = shop.name
    # 简单居中：计算文字宽度
    bbox = draw.textbbox((0, 0), name, font=font_small)
    text_width = bbox[2] - bbox[0]
    x = (400 - text_width) // 2
    draw.text((x, 180), name, font=font_small, fill=text_color)

    # 绘制分类标签
    cat_name = shop.category.name
    bbox_small = draw.textbbox((0, 0), cat_name, font=font_small)
    cat_width = bbox_small[2] - bbox_small[0]
    # 标签背景
    tag_x = (400 - cat_width - 20) // 2
    draw.rounded_rectangle([tag_x, 220, tag_x + cat_width + 20, 250], radius=10, fill=(255, 255, 255))
    draw.text((tag_x + 10, 222), cat_name, font=font_small, fill=text_color)

    # 保存
    filename = f'shop_{shop.pk}.jpg'
    filepath = os.path.join('media', 'shops', filename)
    img.save(filepath, quality=90)
    print(f"[OK] {shop.name} -> {filename}")

print(f"\n完成！共生成 {shops.count()} 张图片")

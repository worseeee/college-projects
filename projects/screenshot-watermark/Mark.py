from PIL import Image, ImageDraw, ImageFont
import math
import os
import time


def add_watermark_batch(input_folder, output_folder,
                        watermark_text="0000000000 刘胜炜",
                        opacity=50, font_size=36, angle=-30,
                        spacing_x_ratio=12, spacing_y_ratio=5):

    if not os.path.exists(input_folder):
        print(f"❌ 输入文件夹不存在: {input_folder}")
        return

    os.makedirs(output_folder, exist_ok=True)

    extensions = ('.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff')

    # ---------- 加载中文字体 ----------
    font = None
    font_paths = [
        "msyh.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for fp in font_paths:
        try:
            font = ImageFont.truetype(fp, font_size)
            print(f"✅ 字体加载成功: {fp}")
            break
        except:
            continue

    if font is None:
        print("❌ 未找到中文字体！")
        return

    # ---------- 获取文件列表 ----------
    files = [f for f in os.listdir(input_folder) if f.lower().endswith(extensions)]

    if not files:
        print(f"❌ 文件夹中没有找到图片: {input_folder}")
        return

    print(f"📂 输入文件夹: {os.path.abspath(input_folder)}")
    print(f"📂 输出文件夹: {os.path.abspath(output_folder)}")
    print(f"📝 水印内容:   {watermark_text}")
    print(f"🔍 找到 {len(files)} 张图片，开始处理...\n")

    start_time = time.time()
    success_count = 0
    fail_count = 0

    # ---------- 逐张处理 ----------
    for i, filename in enumerate(files, 1):
        try:
            img_path = os.path.join(input_folder, filename)
            img = Image.open(img_path).convert("RGBA")
            w, h = img.size

            # 创建大画布
            diagonal = int(math.sqrt(w ** 2 + h ** 2))
            canvas_size = diagonal * 2
            canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(canvas)

            spacing_x = font_size * spacing_x_ratio
            spacing_y = font_size * spacing_y_ratio

            # 平铺绘制水印文字
            for x in range(0, canvas_size, spacing_x):
                for y in range(0, canvas_size, spacing_y):
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            if dx != 0 or dy != 0:
                                draw.text(
                                    (x + dx, y + dy),
                                    watermark_text,
                                    font=font,
                                    fill=(255, 255, 255, opacity // 3)
                                )
                    draw.text(
                        (x, y),
                        watermark_text,
                        font=font,
                        fill=(180, 180, 180, opacity)
                    )

            # 旋转水印画布
            canvas = canvas.rotate(angle, resample=Image.BICUBIC, expand=False)

            cx = canvas.size[0] // 2
            cy = canvas.size[1] // 2
            left = cx - w // 2
            top = cy - h // 2
            crop_box = (left, top, left + w, top + h)
            watermark_layer = canvas.crop(crop_box)

            if watermark_layer.size != (w, h):
                watermark_layer = watermark_layer.resize((w, h), Image.LANCZOS)

            # 合并原图和水印层
            result = Image.alpha_composite(img, watermark_layer)

            # 保存
            output_path = os.path.join(output_folder, filename)
            if filename.lower().endswith(('.jpg', '.jpeg')):
                result = result.convert("RGB")
                result.save(output_path, "JPEG", quality=95)
            elif filename.lower().endswith('.png'):
                result.save(output_path, "PNG")
            elif filename.lower().endswith('.webp'):
                result.save(output_path, "WEBP", quality=95)
            else:
                result = result.convert("RGB")
                result.save(output_path, quality=95)

            success_count += 1
            print(f"  [{i:>3}/{len(files)}] ✅ {filename}  ({w}x{h})")

        except Exception as e:
            fail_count += 1
            print(f"  [{i:>3}/{len(files)}] ❌ {filename}  错误: {e}")

    elapsed = time.time() - start_time
    print(f"\n{'=' * 50}")
    print(f"🎉 全部完成！")
    print(f"   成功: {success_count} 张")
    if fail_count > 0:
        print(f"   失败: {fail_count} 张")
    print(f"   耗时: {elapsed:.1f} 秒")
    print(f"   输出: {os.path.abspath(output_folder)}")
    print(f"{'=' * 50}")


# ================================================================
if __name__ == "__main__":

    add_watermark_batch(
        input_folder   = r"E:\college\Mark\screenshots",
        output_folder  = r"E:\college\Mark\watermarked",
        watermark_text = "0000000000 刘胜炜",
        opacity        = 50,
        font_size      = 36,
        angle          = -30,
        spacing_x_ratio = 12,
        spacing_y_ratio = 5,
    )

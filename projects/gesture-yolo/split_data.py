import os
import shutil
import random

# 【请修改这里】为你的 GestureDataset 文件夹的绝对路径，注意路径里用双斜杠 \\ 或者正斜杠 /
dataset_dir = "dataset"

# 创建训练集和验证集目录
for folder in ['images/train', 'images/val', 'labels/train', 'labels/val']:
    os.makedirs(os.path.join(dataset_dir, folder), exist_ok=True)

# 获取所有图片文件名
images_dir = os.path.join(dataset_dir, 'images')
labels_dir = os.path.join(dataset_dir, 'labels')
all_images = [f for f in os.listdir(images_dir) if f.endswith(('.JPG', '.PNG', '.JPEG'))]

# 随机打乱并按 8:2 划分
random.shuffle(all_images)
split_idx = int(len(all_images) * 0.8)
train_imgs = all_images[:split_idx]
val_imgs = all_images[split_idx:]

def move_files(file_list, split_type):
    for img_name in file_list:
        txt_name = img_name.rsplit('.', 1)[0] + '.txt'
        # 移动图片
        shutil.move(os.path.join(images_dir, img_name), os.path.join(dataset_dir, f'images/{split_type}', img_name))
        # 移动对应的 txt 标注文件 (如果有的话)
        if os.path.exists(os.path.join(labels_dir, txt_name)):
            shutil.move(os.path.join(labels_dir, txt_name), os.path.join(dataset_dir, f'labels/{split_type}', txt_name))

move_files(train_imgs, 'train')
move_files(val_imgs, 'val')

print(f"✅ 数据划分完成！训练集: {len(train_imgs)}张, 验证集: {len(val_imgs)}张。")
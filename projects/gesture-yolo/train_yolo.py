from ultralytics import YOLO

# 加载 YOLOv8 最小的预训练模型作为基础
model = YOLO('yolov8n.pt')

# 开始训练！参数说明：
# data: 指向你的配置文件
# epochs: 训练轮数（手势比较简单，50轮足够了，如果电脑快可以写 100）
# imgsz: 图片输入尺寸（默认640）
# batch: 批次大小（如果报错内存不足/Out of Memory，请改成 8 或 4）
results = model.train(data='dataset/data.yaml', epochs=50, imgsz=640, batch=16)
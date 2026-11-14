import cv2
from ultralytics import YOLO

# ==========================================
# 1. 静态图片推理测试 (Image Inference)
# ==========================================
def test_single_image(image_path):
    print("正在进行单张图片测试...")
    # 加载我们自己训练出来的“最强权重”
    model = YOLO('runs/detect/train/weights/best.pt')
    
    # 对图片进行推理，并自动保存/显示结果
    results = model(image_path, save=True, show=True, conf=0.5)
    print("图片推理完成！")

# ==========================================
# 2. 实时摄像头推理部署 (Real-time Camera)
# ==========================================
def run_realtime_camera():
    print("正在启动实时手势检测，按 'q' 键退出...")
    # 加载模型
    model = YOLO('runs/detect/train/weights/best.pt')
    
    # 调起系统默认摄像头
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("错误：无法打开摄像头！")
        return

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break

        # 将当前帧送入我们训练好的 YOLO 模型进行推理
        # conf=0.25 表示只显示置信度大于 25% 的结果，过滤杂讯
        results = model(frame, conf=0.25)

        # plot() 方法会自动把边框、我们的英文标签(peace, ok等)和置信度画在原图上
        annotated_frame = results[0].plot()

        # 显示合成后的最终画面
        cv2.imshow("My YOLOv8 Custom Gesture AI", annotated_frame)

        # 实时按键监听，按下 'q' 结束进程
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # 如果你想测试单张图片，把你要测试的图片放在同目录下，取消下一行的注释
    # test_single_image('test_gesture.jpg')
    
    # 启动实时摄像头 AI 识别
    run_realtime_camera()
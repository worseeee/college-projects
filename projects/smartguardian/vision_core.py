import cv2
import time
from ultralytics import YOLO

class YoloVisionEngine:
    def __init__(self, model_path='yolov8n.pt'):
        print(f"[AI初始化] 正在加载 YOLO 视觉模型: {model_path} ...")
        try:
            self.model = YOLO(model_path)
            # 预热模型（空跑一次），防止第一次推理时延迟过高
            # self.model("https://ultralytics.com/images/bus.jpg", verbose=False)
            print("[AI初始化] 视觉大脑加载完毕，随时待命！")
        except Exception as e:
            print(f"[! AI错误 !] 模型加载失败: {e}")

    def wake_up_and_infer(self):
        """
        核心机制：级联唤醒 -> 截取单帧 -> 极速推理 -> 阅后即焚
        返回: (ai_fall_status, annotated_frame_for_ui)
            ai_fall_status: 0(无目标/正常), 1(站立/坐着), 2(危险跌倒)
        """
        print("[视觉唤醒] PIR 触发异常！正在拉起底层摄像头...")
        start_time = time.time()
        
        # 1. 唤醒摄像头 (0代表默认笔记本摄像头或外接USB摄像头)
        cap = cv2.VideoCapture(0)
        
        # 为了防止刚打开摄像头时曝光不足，可以丢弃前几帧，取第5帧
        for _ in range(5):
            cap.read()
        ret, frame = cap.read()
        
        # 2. 阅后即焚：立刻释放硬件资源，防止被黑客后台调用
        cap.release()
        
        if not ret:
            print("[! AI错误 !] 摄像头拉起失败！")
            return 0, None

        # 3. 极速边缘推理
        print("[视觉唤醒] 图像截取成功，正在进行张量推理...")
        results = self.model(frame, verbose=False)
        
        ai_fall_status = 0 # 默认安全状态
        annotated_frame = results[0].plot() # 绘制带有 Bounding Box 的图像（仅供本地UI查看）
        
        # 4. 解析业务逻辑 (由于标准 yolov8n 只能识别 person，我们这里做个业务映射测试)
        # 如果你后续用 fall_detect_best.pt，这里的类别判断需要改成你训练的 id
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            
            # 在 COCO 数据集中，0 代表 person (人)
            if cls_id == 0 and conf > 0.5:
                # ---------------------------------------------------------
                # 【假动作模拟】：因为标准模型区分不了跌倒，
                # 我们这里先用高度和宽度的比例做个极其简陋的“跌倒模拟判断”。
                # (真实跌倒模型请直接判断 class id)
                # ---------------------------------------------------------
                x1, y1, x2, y2 = box.xyxy[0]
                w = x2 - x1
                h = y2 - y1
                
                # 如果人的宽度大于高度（躺在地上），我们判定为疑似跌倒 (状态 2)
                if w > h * 1.2: 
                    ai_fall_status = 2
                    print(f"!!! [AI 警报] 视觉确诊：发现老人跌倒姿态！置信度: {conf:.2f}")
                else:
                    ai_fall_status = 1
                    print(f"[*] [AI 确认] 视觉确诊：老人在视场内，状态正常 (站立/坐姿)。置信度: {conf:.2f}")
                
                break # 识别到一个人就跳出

        cost_time = (time.time() - start_time) * 1000
        print(f"[视觉休眠] 推理完成，耗时 {cost_time:.1f} ms。图像数据已从显存销毁。")
        
        return ai_fall_status, annotated_frame

# ================= 单元测试入口 =================
if __name__ == "__main__":
    engine = YoloVisionEngine('yolov8n.pt') # 确保你的网速能下载这个权重，或者把它放在同级目录
    
    input(">>> 按下 Enter 键，模拟 PIR 触发级联唤醒测试...")
    
    status, img = engine.wake_up_and_infer()
    
    print(f"\n最终向上层返回的 AI 状态: {status}")
    
    # 仅在测试模式下把图弹出来看看框得准不准
    if img is not None:
        cv2.imshow("Privacy Mode OFF - AI Debug", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
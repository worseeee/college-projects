import ollama
from ollama import Client
import os
import time

class OllamaHealthExpert:
    def __init__(self, model_name='qwen3', doc_path='patient_record.txt'):
        self.model_name = model_name
        self.doc_path = doc_path
        self.client = Client(host='http://127.0.0.1:11434')
        self.patient_profile = self._load_patient_record()
        print(f"[LLM初始化] 数字全科医生已上线，当前加载模型: {self.model_name}")

    def _load_patient_record(self):
        """加载本地病历文档，作为 RAG 的外部知识输入"""
        if os.path.exists(self.doc_path):
            with open(self.doc_path, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"[LLM初始化] 已成功挂载本地病历文档: {self.doc_path}")
                return content
        else:
            print(f"[! 警告 !] 未找到病历文档 {self.doc_path}，将采用无预设背景模式。")
            return "无既往病史记录。"

    def generate_urgent_sms(self, temp, gas, fall_status):
        """
        方案 4.3 - Prompt模板示例1: 生成百字以内的家属紧急预警短信
        """
        fall_str = "已跌倒" if fall_status == 2 else "未跌倒"
        
        prompt = f"""角色：你是一位资深老年急救医学专家。
任务：根据以下传感器异构数据和老人的基础病历，生成一条发给家属的紧急预警短信。
传感器数据：当前室温 {temp}℃，燃气浓度 {gas}ppm，YOLO视觉状态：{fall_str}。
患者病历：{self.patient_profile}

要求：
1. 语气必须紧急、专业。
2. 字数严格控制在 100 字以内。
3. 必须包含明确的家属干预措施或急救建议。
4. 直接输出短信内容，不要任何寒暄、不要Markdown格式。"""

        print("\n[AI 思考中] 正在生成紧急预警短信...")
        try:
            response = self.client.chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt}
            ])
            return response['message']['content']
        except Exception as e:
            return f"短信生成失败: {e}"

    def generate_diagnostic_report_stream(self, temp, hum, gas, light, fall_status):
        """
        方案 4.3 - Prompt模板示例2: 生成综合健康诊断报告 (采用流式输出 stream=True)
        返回一个生成器，UI 界面可以通过迭代它来实现“打字机”效果。
        """
        fall_str = "确认跌倒" if fall_status == 2 else ("站立/坐着" if fall_status == 1 else "未见异常")
        
        prompt = f"""角色：你是一位耐心的全科医生。
任务：结合患者既往病史与当前的居家物联网环境数据，进行全面的健康与风险研判。
环境数据：室温 {temp}℃，湿度 {hum}%，燃气 {gas}ppm，光照 {light}Lux，视觉动作核查：{fall_str}。
病历参考：{self.patient_profile}

要求：
1. 结合患者的特定疾病（如高血压、阿尔茨海默症等），分析当前环境（如温度骤降、燃气异常等）对他的具体潜在危害。
2. 给出逻辑严密的医护建议。
3. 使用 Markdown 格式进行排版，分为“现状分析”、“潜在风险”、“医护建议”三个段落。
4. 语言要有同理心和温度，总字数不超过 300 字。"""

        print("\n[AI 思考中] 正在流式生成详细研判报告...\n")
        try:
            # 开启 stream=True，大模型吐出一个字我们就拿一个字
            stream = self.client.chat(model=self.model_name, 
                                 messages=[{'role': 'user', 'content': prompt}],
                                 stream=True)
            for chunk in stream:
                # 使用 yield 将每个字弹出去，供外层 UI 接收
                yield chunk['message']['content']
        except Exception as e:
            yield f"\n[大模型推理中断]: {e}"

# ================= 单元测试入口 =================
if __name__ == "__main__":
    # 请确保你在命令行已经运行了 Ollama，且拥有 qwen 模型
    # 如果你本地是其他模型，请修改 model_name='llama3' 或其他你拥有的模型名
    llm = OllamaHealthExpert(model_name='qwen3')
    
    # 模拟一次深夜寒冷环境下的跌倒事件
    test_temp = 12
    test_hum = 45
    test_gas = 0
    test_light = 15
    test_fall = 2
    
    # 测试 1：生成短短信
    sms = llm.generate_urgent_sms(test_temp, test_gas, test_fall)
    print("================== 极危短信输出 ==================")
    print(sms)
    print("==================================================")
    
    time.sleep(1)
    
    # 测试 2：测试流式长文本输出
    print("\n================== 综合诊断报告 (流式) ==================")
    report_generator = llm.generate_diagnostic_report_stream(test_temp, test_hum, test_gas, test_light, test_fall)
    
    # 模拟 UI 接收流式字符，实现打字机效果
    for char in report_generator:
        print(char, end='', flush=True) 
    print("\n========================================================")
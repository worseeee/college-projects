import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import requests
import threading
import queue
import json
import time

# ================= 配置常量 =================
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3"  # 请确保你本地已 pull 该模型，也可改为你本地的 llama3 等

# ================= 核心引擎类 =================
class OllamaClient:
    def __init__(self):
        self.is_stopped = False

    def generate_stream(self, prompt, output_queue):
        """流式请求大模型，并将结果推入队列"""
        self.is_stopped = False
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": True
        }
        
        start_time = time.time()
        token_count = 0

        try:
            # 核心原理 1：使用 stream=True 发起流式请求
            response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=120)
            response.raise_for_status()

            for line in response.iter_lines():
                if self.is_stopped:
                    output_queue.put({"type": "stopped", "msg": "\n[已强制停止]"})
                    break
                
                if line:
                    data = json.loads(line)
                    word = data.get("response", "")
                    token_count += 1
                    
                    # 核心原理 2：通过队列将数据安全地发给 UI 线程
                    output_queue.put({"type": "text", "msg": word})
                    
                    if data.get("done", False):
                        # 计算最终速度
                        total_time = time.time() - start_time
                        speed = token_count / total_time if total_time > 0 else 0
                        output_queue.put({"type": "done", "speed": speed})
                        break

        except requests.exceptions.RequestException as e:
            output_queue.put({"type": "error", "msg": f"\n[请求失败]: {e}\n请确保本地 Ollama 服务已启动。"})

    def stop(self):
        self.is_stopped = True

# ================= UI 界面类 =================
class LocalAILabApp:
    def __init__(self, root):
        self.root = root
        self.root.title("本地 AI 学习实验室 - Local AI Learning Lab")
        self.root.geometry("900x700")

        self.client = OllamaClient()
        self.msg_queue = queue.Queue()
        self.is_generating = False

        self._build_ui()

    def _build_ui(self):
        # 1. 顶部状态栏
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_label = tk.Label(top_frame, text=f"模型: {MODEL_NAME} | 状态: 就绪 | 速度: 0.00 tok/s")
        self.status_label.pack(side=tk.LEFT)
        
        self.btn_stop = tk.Button(top_frame, text="停止生成", command=self.stop_generation, state=tk.DISABLED, bg="#ffcccc")
        self.btn_stop.pack(side=tk.RIGHT)

        # 2. 核心标签页
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建 6 个 Tab
        self.tab_chat = ttk.Frame(self.notebook)
        self.tab_summary = ttk.Frame(self.notebook)
        self.tab_qa = ttk.Frame(self.notebook)
        self.tab_code = ttk.Frame(self.notebook)
        self.tab_doc = ttk.Frame(self.notebook)
        self.tab_prompt = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_chat, text="聊天助手")
        self.notebook.add(self.tab_summary, text="文章总结")
        self.notebook.add(self.tab_qa, text="学习问答")
        self.notebook.add(self.tab_code, text="代码助手")
        self.notebook.add(self.tab_doc, text="资料问答")
        self.notebook.add(self.tab_prompt, text="Prompt 实验")

        # --- 初始化各个 Tab 的内容 ---
        self._init_chat_tab()
        self._init_summary_tab()
        self._init_qa_tab()
        self._init_code_tab()
        self._init_doc_tab()
        self._init_prompt_tab()

    # =========== 通用 UI 组件构建方法 ===========
    def create_text_area(self, parent):
        """创建只读的输出文本框"""
        text_area = scrolledtext.ScrolledText(parent, wrap=tk.WORD, state=tk.DISABLED, font=("微软雅黑", 10))
        text_area.pack(fill=tk.BOTH, expand=True, pady=5)
        return text_area

    def create_input_area(self, parent, send_command):
        """创建输入框和按钮栏"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        
        input_text = tk.Text(frame, height=4, font=("微软雅黑", 10))
        input_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        btn_frame = tk.Frame(frame)
        btn_frame.pack(side=tk.RIGHT)
        
        tk.Button(btn_frame, text="发送", command=send_command, width=10, bg="#cceeff").pack(pady=2)
        tk.Button(btn_frame, text="清空输入", command=lambda: input_text.delete("1.0", tk.END), width=10).pack(pady=2)
        
        return input_text

    # =========== 具体的 Tab 界面设计 (Prompt 工程体现处) ===========
    def _init_chat_tab(self):
        tk.Label(self.tab_chat, text="本功能展示：本地大模型无前置设定的自由聊天。").pack(anchor=tk.W)
        self.chat_out = self.create_text_area(self.tab_chat)
        self.chat_in = self.create_input_area(self.tab_chat, lambda: self.run_prompt(self.chat_in.get("1.0", tk.END).strip(), self.chat_out))

    def _init_summary_tab(self):
        tk.Label(self.tab_summary, text="请输入长文本，AI 将提取核心摘要。").pack(anchor=tk.W)
        self.sum_out = self.create_text_area(self.tab_summary)
        self.sum_in = self.create_input_area(self.tab_summary, lambda: self.run_prompt(
            f"请帮我总结以下文章的核心观点，要求条理清晰：\n{self.sum_in.get('1.0', tk.END).strip()}", self.sum_out))

    def _init_qa_tab(self):
        top = tk.Frame(self.tab_qa)
        top.pack(fill=tk.X)
        tk.Label(top, text="选择学科模式:").pack(side=tk.LEFT)
        self.subject_cb = ttk.Combobox(top, values=["计算机科学", "物理学", "哲学", "通俗解释(给小孩听)"], state="readonly")
        self.subject_cb.current(0)
        self.subject_cb.pack(side=tk.LEFT, padx=5)
        
        self.qa_out = self.create_text_area(self.tab_qa)
        self.qa_in = self.create_input_area(self.tab_qa, lambda: self.run_prompt(
            f"你现在是一位{self.subject_cb.get()}专家。请专业、准确地回答以下问题：\n{self.qa_in.get('1.0', tk.END).strip()}", self.qa_out))

    def _init_code_tab(self):
        top = tk.Frame(self.tab_code)
        top.pack(fill=tk.X)
        tk.Label(top, text="选择任务类型:").pack(side=tk.LEFT)
        self.code_task_cb = ttk.Combobox(top, values=["解释代码", "寻找 Bug", "代码重构"], state="readonly")
        self.code_task_cb.current(0)
        self.code_task_cb.pack(side=tk.LEFT, padx=5)
        
        self.code_out = self.create_text_area(self.tab_code)
        self.code_in = self.create_input_area(self.tab_code, lambda: self.run_prompt(
            f"请执行【{self.code_task_cb.get()}】任务，分析以下代码：\n{self.code_in.get('1.0', tk.END).strip()}", self.code_out))

    def _init_doc_tab(self):
        top = tk.Frame(self.tab_doc)
        top.pack(fill=tk.X)
        tk.Button(top, text="加载本地 TXT 文档", command=self._load_txt).pack(side=tk.LEFT)
        self.doc_path_lbl = tk.Label(top, text="未加载文档")
        self.doc_path_lbl.pack(side=tk.LEFT, padx=10)
        
        self.doc_content = ""
        self.doc_out = self.create_text_area(self.tab_doc)
        self.doc_in = self.create_input_area(self.tab_doc, lambda: self.run_prompt(
            f"基于以下参考资料回答问题：\n【资料内容】:\n{self.doc_content[:1500]}\n\n【问题】: {self.doc_in.get('1.0', tk.END).strip()}", self.doc_out) 
            if self.doc_content else messagebox.showwarning("警告", "请先加载 TXT 文档！"))

    def _load_txt(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if filepath:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                self.doc_content = f.read()
            self.doc_path_lbl.config(text=f"已加载: {filepath.split('/')[-1]}")
            messagebox.showinfo("成功", "文档加载成功，您现在可以针对文档提问了！")

    def _init_prompt_tab(self):
        top = tk.Frame(self.tab_prompt)
        top.pack(fill=tk.X)
        
        tk.Label(top, text="设定角色:").grid(row=0, column=0, sticky=tk.W)
        self.pr_role = tk.Entry(top, width=50); self.pr_role.insert(0, "资深物联网工程师")
        self.pr_role.grid(row=0, column=1, pady=2)
        
        tk.Label(top, text="任务要求:").grid(row=1, column=0, sticky=tk.W)
        self.pr_task = tk.Entry(top, width=50); self.pr_task.insert(0, "列出物联网架构的三个层级")
        self.pr_task.grid(row=1, column=1, pady=2)
        
        tk.Label(top, text="输出格式:").grid(row=2, column=0, sticky=tk.W)
        self.pr_format = tk.Entry(top, width=50); self.pr_format.insert(0, "使用 Markdown 表格输出")
        self.pr_format.grid(row=2, column=1, pady=2)

        self.pr_out = self.create_text_area(self.tab_prompt)
        tk.Button(self.tab_prompt, text="执行自定义 Prompt", bg="#cceeff", command=lambda: self.run_prompt(
            f"角色：{self.pr_role.get()}\n任务：{self.pr_task.get()}\n格式：{self.pr_format.get()}", self.pr_out)).pack(pady=5)

    # =========== 核心调度与通信逻辑 ===========
    def run_prompt(self, prompt, target_text_area):
        if not prompt.strip(): return
        if self.is_generating:
            messagebox.showwarning("提示", "模型正在生成中，请稍后或点击停止。")
            return

        self.is_generating = True
        self.current_target_area = target_text_area
        self.btn_stop.config(state=tk.NORMAL)
        self.status_label.config(text=f"模型: {MODEL_NAME} | 状态: 生成中... | 速度: 计算中")

        # 准备 UI
        target_text_area.config(state=tk.NORMAL)
        target_text_area.insert(tk.END, f"\n\n👤 你:\n{prompt}\n\n🤖 AI:\n")
        target_text_area.see(tk.END)
        target_text_area.config(state=tk.DISABLED)

        # 核心原理 3：开启子线程发起请求，防止 UI 卡死
        threading.Thread(target=self.client.generate_stream, args=(prompt, self.msg_queue), daemon=True).start()
        
        # 启动 UI 轮询
        self.root.after(50, self.check_queue)

    def check_queue(self):
        """核心原理 4：主线程定时从队列中取字，安全更新 UI"""
        try:
            while True:
                msg_data = self.msg_queue.get_nowait()
                msg_type = msg_data.get("type")

                if msg_type == "text":
                    self.current_target_area.config(state=tk.NORMAL)
                    self.current_target_area.insert(tk.END, msg_data["msg"])
                    self.current_target_area.see(tk.END)
                    self.current_target_area.config(state=tk.DISABLED)
                
                elif msg_type == "done":
                    speed = msg_data.get("speed", 0)
                    self._reset_ui_state(f"状态: 完成 | 速度: {speed:.2f} tok/s")
                    return
                
                elif msg_type == "stopped":
                    self.current_target_area.config(state=tk.NORMAL)
                    self.current_target_area.insert(tk.END, msg_data["msg"])
                    self.current_target_area.config(state=tk.DISABLED)
                    self._reset_ui_state("状态: 已停止 | 速度: -- tok/s")
                    return
                
                elif msg_type == "error":
                    self.current_target_area.config(state=tk.NORMAL)
                    self.current_target_area.insert(tk.END, msg_data["msg"])
                    self.current_target_area.config(state=tk.DISABLED)
                    self._reset_ui_state("状态: 错误 | 速度: -- tok/s")
                    return

        except queue.Empty:
            pass

        # 如果还没生成完，50ms 后继续检查队列
        if self.is_generating:
            self.root.after(50, self.check_queue)

    def stop_generation(self):
        self.client.stop()
        self.btn_stop.config(state=tk.DISABLED)

    def _reset_ui_state(self, status_text):
        self.is_generating = False
        self.btn_stop.config(state=tk.DISABLED)
        self.status_label.config(text=f"模型: {MODEL_NAME} | {status_text}")

if __name__ == "__main__":
    root = tk.Tk()
    # 使用稍微现代一点的 ttk 风格
    style = ttk.Style()
    if "clam" in style.theme_names():
        style.theme_use("clam")
    app = LocalAILabApp(root)
    root.mainloop()
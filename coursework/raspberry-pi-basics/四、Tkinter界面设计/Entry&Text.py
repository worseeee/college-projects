import tkinter as tk

root = tk.Tk()
root.title("Entry和Text控件示例 - 刘胜炜 0000000000")
root.geometry("400x300")

tk.Label(root, text="用户名:").pack(pady=5)
entry = tk.Entry(root, width=30)
entry.pack(pady=5)

tk.Label(root, text="备注信息:").pack(pady=5)
text = tk.Text(root, width=30, height=5)
text.pack(pady=5)

watermark = tk.Label(root, text="刘胜炜-0000000000", fg="gray", font=("Arial", 8))
watermark.pack(side=tk.BOTTOM)

root.mainloop()

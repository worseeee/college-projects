import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Listbox和Combobox示例 - 刘胜炜 0000000000")
root.geometry("400x350")

tk.Label(root, text="Listbox列表框:").pack(pady=5)
listbox = tk.Listbox(root, height=4)
items = ["选项1", "选项2", "选项3", "选项4"]
for item in items:
    listbox.insert(tk.END, item)
listbox.pack(pady=5)

tk.Label(root, text="Combobox下拉框:").pack(pady=5)
combo = ttk.Combobox(root, values=["北京", "上海", "广州", "深圳"], state="readonly")
combo.current(0)
combo.pack(pady=5)

watermark = tk.Label(root, text="刘胜炜-0000000000", fg="gray", font=("Arial", 8))
watermark.pack(side=tk.BOTTOM)

root.mainloop()

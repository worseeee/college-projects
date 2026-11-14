import tkinter as tk

root = tk.Tk()
root.title("Menu和Scrollbar示例 - 刘胜炜 0000000000")
root.geometry("400x300")

menubar = tk.Menu(root)
root.config(menu=menubar)

file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="文件", menu=file_menu)
file_menu.add_command(label="新建")
file_menu.add_command(label="打开")
file_menu.add_separator()
file_menu.add_command(label="退出", command=root.quit)

frame = tk.Frame(root)
frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

text = tk.Text(frame, yscrollcommand=scrollbar.set)
text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=text.yview)

for i in range(50):
    text.insert(tk.END, f"这是第{i+1}行文本\n")

watermark = tk.Label(root, text="刘胜炜-0000000000", fg="gray", font=("Arial", 8))
watermark.place(x=10, y=280)

root.mainloop()

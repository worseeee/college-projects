import tkinter as tk

root = tk.Tk()
root.title("Message控件示例 - 刘胜炜 0000000000")
root.geometry("400x300")

message = tk.Message(root, text="这是Message控件，可以显示较长的文本内容，会自动换行处理。适合显示提示信息。", 
                     width=300, font=("Arial", 11))
message.pack(pady=20)

watermark = tk.Label(root, text="刘胜炜-0000000000", fg="gray", font=("Arial", 8))
watermark.pack(side=tk.BOTTOM)

root.mainloop()

import tkinter as tk

root = tk.Tk()
root.title("Label控件示例 - 刘胜炜 0000000000")
root.geometry("400x300")

label1 = tk.Label(root, text="这是一个普通标签", font=("Arial", 12))
label1.pack(pady=10)

label2 = tk.Label(root, text="带颜色的标签", bg="lightblue", fg="red", font=("Arial", 14))
label2.pack(pady=10)

watermark = tk.Label(root, text="刘胜炜-0000000000", fg="gray", font=("Arial", 8))
watermark.pack(side=tk.BOTTOM)

root.mainloop()

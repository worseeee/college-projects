import tkinter as tk

root = tk.Tk()
root.title("Radiobutton和Checkbutton示例 - 刘胜炜 0000000000")
root.geometry("400x300")

tk.Label(root, text="性别选择(Radiobutton):").pack(pady=5)
gender = tk.StringVar(value="男")
tk.Radiobutton(root, text="男", variable=gender, value="男").pack()
tk.Radiobutton(root, text="女", variable=gender, value="女").pack()

tk.Label(root, text="兴趣爱好(Checkbutton):").pack(pady=10)
hobby1 = tk.IntVar()
hobby2 = tk.IntVar()
tk.Checkbutton(root, text="运动", variable=hobby1).pack()
tk.Checkbutton(root, text="阅读", variable=hobby2).pack()

watermark = tk.Label(root, text="刘胜炜-0000000000", fg="gray", font=("Arial", 8))
watermark.pack(side=tk.BOTTOM)

root.mainloop()

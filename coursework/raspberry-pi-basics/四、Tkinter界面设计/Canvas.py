import tkinter as tk

root = tk.Tk()
root.title("Canvas控件示例 - 刘胜炜 0000000000")
root.geometry("400x400")

canvas = tk.Canvas(root, width=300, height=250, bg="white")
canvas.pack(pady=10)

canvas.create_line(50, 50, 250, 50, fill="blue", width=2)
canvas.create_rectangle(50, 80, 150, 150, fill="lightblue", outline="blue")
canvas.create_oval(180, 80, 250, 150, fill="lightgreen", outline="green")

watermark = tk.Label(root, text="刘胜炜-0000000000", fg="gray", font=("Arial", 8))
watermark.pack(side=tk.BOTTOM)

root.mainloop()

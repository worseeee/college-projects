import tkinter as tk

def pack_demo():
    win = tk.Toplevel()
    win.title("Pack布局示例 - 刘胜炜 0000000000")
    win.geometry("300x200")
    
    tk.Label(win, text="顶部", bg="red").pack(side=tk.TOP, fill=tk.X)
    tk.Label(win, text="底部", bg="blue").pack(side=tk.BOTTOM, fill=tk.X)
    tk.Label(win, text="左侧", bg="green").pack(side=tk.LEFT, fill=tk.Y)
    tk.Label(win, text="右侧", bg="yellow").pack(side=tk.RIGHT, fill=tk.Y)

def grid_demo():
    win = tk.Toplevel()
    win.title("Grid布局示例 - 刘胜炜 0000000000")
    win.geometry("300x200")
    
    for i in range(3):
        for j in range(3):
            tk.Label(win, text=f"({i},{j})", borderwidth=1, relief="solid", 
                    width=10, height=3).grid(row=i, column=j, padx=5, pady=5)

def place_demo():
    win = tk.Toplevel()
    win.title("Place布局示例 - 刘胜炜 0000000000")
    win.geometry("300x200")
    
    tk.Label(win, text="绝对定位(50,50)", bg="lightblue").place(x=50, y=50)
    tk.Label(win, text="相对定位(0.5,0.5)", bg="lightgreen").place(relx=0.5, rely=0.5, anchor="center")

root = tk.Tk()
root.title("布局管理器演示 - 刘胜炜 0000000000")
root.geometry("300x200")

tk.Button(root, text="Pack布局", command=pack_demo, width=15).pack(pady=10)
tk.Button(root, text="Grid布局", command=grid_demo, width=15).pack(pady=10)
tk.Button(root, text="Place布局", command=place_demo, width=15).pack(pady=10)

watermark = tk.Label(root, text="刘胜炜-0000000000", fg="gray", font=("Arial", 8))
watermark.pack(side=tk.BOTTOM)

root.mainloop()

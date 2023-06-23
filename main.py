# base_info.py中的内容为functions_map = [('字符格式化', 'format_string.py'),
# 其中，functions_map 中数组每一个元素的第一个为display_name，第二个为file_path。
# 通过遍历functions_map 数组中的元素，对于每一个元素都创建一个按钮，
# 其中，按钮显示的内容就是元素的display_name，点击按钮后调用file_path函数
# 窗口最小为200x200，并且启动时显示在屏幕中继位置，上下两个button之间添加一个小间距
# 按钮横向排列并且每行最多显示5个按钮

import tkinter as tk
import importlib
import os
import sys
from tkinter import *
from tkinter.ttk import *
import tkinter.messagebox as messagebox
import pyperclip
import unicodedata
import subprocess
import threading

# 将需要动态加载的模块路径添加到 sys.path 中
sys.path.append('plugin')

def call_function(file_path):
    prev_path = os.getcwd()
    print(prev_path)
    if file_path.endswith('.exe'):
        t = threading.Thread(target=subprocess.run, args=[os.path.join('plugin', file_path),]) 
        # 守护线程
        t.setDaemon(True) 
        # 启动线程
        t.start()
    else:
        module_name = file_path.replace("/", ".").replace("\\", ".").rstrip(".py")
        print(module_name)
        function_name = "process"
        try:
            module = importlib.import_module(module_name)
            function = getattr(module, function_name)
            function()
        except Exception as e:
            messagebox.showerror('调用失败', str(e))


# Create a Tkinter window
root = tk.Tk()
root.minsize(400, 200)
root.title("我的小工具集")


with open('configure.txt', 'r', encoding='utf8') as f:
    functions_map = [list(map(lambda x:x.strip(), pair.split(','))) for pair in f.read().strip().split('\n')]

row, col, count = 0, 0, 0
# Create a button for each function in functions_map
for display_name, file_path in functions_map:
    button = tk.Button(root, text=display_name, command=lambda file_path=file_path: call_function(file_path))
    button.grid(row=row, column=col, padx=5, pady=5)
    count += 1
    if count == 5:
        count = 0
        row += 1
        col = 0
    else:
        col += 1

# Calculate the position of the window
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width - root.winfo_reqwidth()) / 2
y = (screen_height - root.winfo_reqheight()) / 2
# Set the position of the window
root.geometry("+%d+%d" % (x, y))

# Start the main loop
root.mainloop()


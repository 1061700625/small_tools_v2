import tkinter as tk
from tkinter import ttk
import pyperclip
import unicodedata
import re
from tkinter import messagebox

class StringFormatterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("文本格式化工具")
        self.configure(bg="#f0f0f0")
        # 窗口大小设置
        self.app_width = 600
        self.app_height = 400
        # 获取屏幕尺寸以计算布局参数，使窗口居中
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.app_width) / 2
        y = (screen_height - self.app_height) / 2
        self.geometry(f'{self.app_width}x{self.app_height}+{int(x)}+{int(y)}')  # 设置窗口尺寸及位置
        # 设置样式
        style = ttk.Style(self)
        style.configure("TButton", padding=6)
        style.configure("TLabel", background="#f0f0f0")
        style.configure("TFrame", background="#f0f0f0")

        frame = ttk.Frame(self)
        frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # 文本框用于显示原始数据
        self.input_text = tk.Text(frame, height=8, width=50)
        self.input_text.pack(pady=(10, 10), fill=tk.BOTH, expand=True)

        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, expand=False)

        self.btn_clear = ttk.Button(button_frame, text="清空内容", command=self.clear_texts)
        self.btn_clear.pack(side=tk.LEFT, padx=10, pady=10)

        self.btn_remove_spaces = ttk.Button(button_frame, text="去除空格", command=self.remove_spaces)
        self.btn_remove_spaces.pack(side=tk.LEFT, padx=10)

        self.btn_remove_newlines = ttk.Button(button_frame, text="去除换行", command=self.remove_newlines)
        self.btn_remove_newlines.pack(side=tk.LEFT, padx=10)

        self.btn_format = ttk.Button(button_frame, text="去格式化", command=self.format_text)
        self.btn_format.pack(side=tk.LEFT, padx=10)

        self.btn_copy = ttk.Button(button_frame, text="复制内容", command=self.copy_text)
        self.btn_copy.pack(side=tk.LEFT, padx=10)

        # 文本框用于显示处理后的数据
        self.output_text = tk.Text(frame, height=8, width=50)
        self.output_text.pack(pady=(10, 10), fill=tk.BOTH, expand=True)

    def clear_texts(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)

    def remove_spaces(self):
        text = self.input_text.get("1.0", tk.END).replace(" ", "")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)

    def remove_newlines(self):
        text = self.input_text.get("1.0", tk.END).replace("\n", "")
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)

    def format_text(self):
        text = self.input_text.get("1.0", tk.END)
        text = self.fullwidth_to_halfwidth(text)
        text = ''.join([char if ord(char) < 128 or self.is_chinese_or_punctuation(char) else ' ' for char in text])
        text = re.sub(r'\s+', ' ', text).strip()
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert("1.0", text)

    def fullwidth_to_halfwidth(self, s):
        return ''.join([chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c for c in s])

    def is_chinese_or_punctuation(self, char):
        category = unicodedata.category(char)
        return 'Lo' in category or 'P' in category

    def copy_text(self):
        text = self.output_text.get("1.0", tk.END)
        pyperclip.copy(text)
        messagebox.showinfo("复制到剪切板", "内容已复制到系统剪切板！")

def main():
    app = StringFormatterApp()
    app.mainloop()

if __name__ == "__main__":
    main()

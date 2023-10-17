# Python和Tkinter：
# 运行后，弹出窗口。
# 窗口内包括2个比较大的文本输入框input_text1、input_text2和2个按钮btn_convert、btn_copy，按钮上分别显示的是“转换”、“复制”字样。
# 用户输入一段文字到文本输入框input_text1中，点击“转换”按钮后，自动将文字中的空格都去掉，然后将处理后的结果显示到文本输入框input_text2。
# 用户通过点击“复制”按钮后，并将结果复制到系统剪切板上。
# 再在“复制”按钮边上添加一个“格式化”按钮btn_format，用户点击该按钮后，将input_text2中的内容的样式转为半角字符。
# 再在“转换”按钮边上添加一个“清空”按钮btn_clear，用户点击该按钮后，将input_text1和input_text2中的内容全部清空。

import re
from tkinter import *
from tkinter.ttk import *
from typing import Dict
import tkinter.messagebox as messagebox
import pyperclip
import unicodedata

class WinGUI(Tk):
    widget_dic: Dict[str, Widget] = {}
    def __init__(self):
        super().__init__()
        self.__win()
        self.widget_dic["tk_input_text1"] = self.__tk_input_text1(self)
        self.widget_dic["tk_button_convert"] = self.__tk_button_convert(self)
        self.widget_dic["tk_button_clear"] = self.__tk_button_clear(self)
        self.widget_dic["tk_input_text2"] = self.__tk_input_text2(self)
        self.widget_dic["tk_button_copy"] = self.__tk_button_copy(self)
        self.widget_dic["tk_button_format"] = self.__tk_button_format(self)

    def __win(self):
        self.title("格式化字符串")
        # 设置窗口大小、居中
        width = 500
        height = 470
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.resizable(width=False, height=False)

        # 自动隐藏滚动条
    def scrollbar_autohide(self,bar,widget):
        self.__scrollbar_hide(bar,widget)
        widget.bind("<Enter>", lambda e: self.__scrollbar_show(bar,widget))
        bar.bind("<Enter>", lambda e: self.__scrollbar_show(bar,widget))
        widget.bind("<Leave>", lambda e: self.__scrollbar_hide(bar,widget))
        bar.bind("<Leave>", lambda e: self.__scrollbar_hide(bar,widget))
    
    def __scrollbar_show(self,bar,widget):
        bar.lift(widget)

    def __scrollbar_hide(self,bar,widget):
        bar.lower(widget)
        
    def __tk_input_text1(self,parent):
        ipt = Text(parent, wrap=WORD)
        ipt.place(x=20, y=20, width=459, height=138)
        return ipt

    def __tk_button_convert(self,parent):
        btn = Button(parent, text="去除空格")
        btn.place(x=100, y=180, width=102, height=40)
        return btn

    def __tk_button_clear(self,parent):
        btn = Button(parent, text="清空内容")
        btn.place(x=300, y=180, width=102, height=40)
        return btn

    def __tk_input_text2(self,parent):
        ipt = Text(parent, wrap=WORD)
        ipt.place(x=20, y=240, width=460, height=140)
        return ipt

    def __tk_button_copy(self,parent):
        btn = Button(parent, text="复制内容")
        btn.place(x=100, y=400, width=102, height=40)
        return btn

    def __tk_button_format(self,parent):
        btn = Button(parent, text="去格式化")
        btn.place(x=300, y=400, width=102, height=40)
        return btn


class Win(WinGUI):
    def __init__(self):
        super().__init__()
        self.__event_bind()

    def convert_text(self,evt):
        input_text1 = self.widget_dic["tk_input_text1"]
        input_text2 = self.widget_dic["tk_input_text2"]
        text = input_text1.get("1.0", "end-1c")  # 获取输入文本框中的内容
        converted_text = text.replace(" ", "")  # 去掉所有空格
        input_text2.delete("1.0", "end")  # 清空输出文本框
        input_text2.insert("1.0", converted_text)  # 在输出文本框中显示处理后的结果

    def copy_text(self,evt):
        input_text2 = self.widget_dic["tk_input_text2"]
        text = input_text2.get("1.0", "end-1c")  # 获取输出文本框中的内容
        pyperclip.copy(text)  # 将结果复制到系统剪切板
        messagebox.showinfo("提示", "已复制到剪切板！")  # 弹出提示框

    def format_text(self,evt):
        def fullwidth_to_halfwidth(s):
            """Convert full-width characters to half-width."""
            return ''.join([chr(ord(c) - 0xFEE0) if 0xFF01 <= ord(c) <= 0xFF5E else c for c in s])
        input_text2 = self.widget_dic["tk_input_text2"]
        text = input_text2.get("1.0", "end-1c")  # 获取输入框2中的内容
        text = fullwidth_to_halfwidth(text)
        # Replace non-ASCII characters (excluding Chinese characters) with a space
        text = re.sub(r'[^\x00-\x7F\u4e00-\u9fa5]+', ' ', text)
        # Replace multiple spaces with a single space
        text = re.sub(r'\s+', ' ', text).strip()
        input_text2.delete("1.0", "end")  # 清空输入框2
        input_text2.insert("end", text)  # 在输入框2中显示处理后的内容

    def clear_text(self,evt):
        input_text1 = self.widget_dic["tk_input_text1"]
        input_text2 = self.widget_dic["tk_input_text2"]
        input_text1.delete("1.0", "end")  # 清空输入框1
        input_text2.delete("1.0", "end")  # 清空输入框2
    
    def __event_bind(self):
        self.widget_dic["tk_button_convert"].bind('<Button-1>',self.convert_text)
        self.widget_dic["tk_button_clear"].bind('<Button-1>',self.clear_text)
        self.widget_dic["tk_button_copy"].bind('<Button-1>',self.copy_text)
        self.widget_dic["tk_button_format"].bind('<Button-1>',self.format_text)

def process():
    win = Win()
    win.mainloop()
if __name__ == "__main__":
    process()

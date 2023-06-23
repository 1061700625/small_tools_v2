import tkinter as tk
import datetime
import math
import locale
import os, sys
from tkinter.colorchooser import askcolor
import webbrowser
import tkinter.messagebox as messagebox
import tkinter.ttk as ttk
import tkcalendar
import babel.numbers
import requests
import tkinter.simpledialog
import winreg

# Set the locale to use UTF-8 encoding
locale.setlocale(locale.LC_ALL, 'en_US.utf8')
VERSION = '20230406'
CONFIG_REG_PATH = r'SOFTWARE\desktop_clock\Settings'


class TransparentWindow(tk.Tk):
    def __init__(self, text_file=None):
        super().__init__()
        self.attributes('-alpha', 1) # 设置窗口透明度
        # self.attributes('-topmost', True) # 窗口置顶
        # self.attributes('-transparentcolor', '#000000')
        self.overrideredirect(True) # 去掉窗口边框
        self.locked = False # 初始化锁定状态
        self.mouse_x = 0
        self.mouse_y = 0
        self.config(bg='#000000', highlightthickness=0, bd=0)
        self.window_width = 400
        self.window_height = 100

        # # 获取屏幕尺寸和窗口尺寸，使窗口居中
        # screen_width = self.winfo_screenwidth()
        # screen_height = self.winfo_screenheight()
        # x = (screen_width - self.window_width) // 2
        # y = (screen_height - self.window_height) // 2
        # self.geometry('{}x{}+{}+{}'.format(self.window_width, self.window_height, x, y))
        

        # 添加日期时间标签
        self.datetime_label = tk.Label(self, text='', font=('Arial', 20), fg='#FFFFFF', bg='#000000')
        self.datetime_label.place(relx=0.5, y=20, anchor='center')

        # 提示标签
        self.note_label = tk.Label(self, text='123', font=('Arial', 14), fg='#FFFFFF', bg='#000000')
        self.note_label.place(relx=0.5, y=50, anchor='center')

        # 文本标签
        self.text_label = tk.Label(self, text='', font=('Arial', 14), fg='#FFFFFF', bg='#000000')
        self.text_label.place(relx=0.5, y=80, anchor='center')

        # 添加锁定按钮
        self.lock_button = tk.Button(self, text='锁定', font=('Arial', 10), command=self.toggle_lock)
        self.toggle_lock_button(True)
        self.toggle_lock_button(False)

        # 添加解锁按钮
        self.unlock_button = tk.Button(self, text='解除锁定', font=('Arial', 10), command=self.toggle_lock)
        self.toggle_unlock_button(True)
        self.toggle_unlock_button(False)

        # 绑定鼠标事件
        self.bind('<Button-1>', self.on_left_button_down)
        self.bind('<ButtonRelease-1>', self.on_left_button_up)
        self.bind('<B1-Motion>', self.on_mouse_drag)
        self.bind('<Enter>', self.on_mouse_enter)
        self.bind('<Leave>', self.on_mouse_leave)

        # 创建右键菜单
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="退出应用", command=self.destroy)
        # 添加“置顶”子菜单
        self.menu.add_command(label="窗口置顶", command=self.topmost_on)
        # 添加“改变颜色”子菜单
        self.menu.add_command(label="修改颜色", command=self.choose_color)
        # 添加“修改日期”子菜单
        self.menu.add_command(label="修改日期", command=self.modify_date)
        # 添加“修改note”子菜单
        self.menu.add_command(label='修改Note', command=self.edit_text_labele)
        # 添加“开机自启动”子菜单
        self.menu.add_command(label="开机自启", command=self.toggle_startup)
        # 添加“恢复出厂设置”子菜单
        self.menu.add_command(label="恢复设置", command=self.init_config_to_registry)
        # 添加“关于”子菜单
        self.menu.add_command(label="关于我们", command=self.about_me)
        self.bind("<Button-3>", self.show_menu)

        self.update_config_from_registry()
        # 定时更新日期时间标签
        self.update_datetime()
        # 定时更新text标签
        self.update_text_label()
        # 定时更新note标签
        self.update_note_label()
        self.check_version()
        
    

    def update_config_from_registry(self):
        # Get settings from registry or set default values
        self.start_date = self.get_value_from_registry('start_date', '2023/2/20', write=True)
        self.end_date = self.get_value_from_registry('end_date', '2023/7/9', write=True)
        startup = self.get_value_from_registry('startup', False)
        self.menu.entryconfig(5, label='取消自动' if startup else '开机自启')
        topmost = self.get_value_from_registry('topmost', False)
        self.attributes('-topmost', True if topmost else False)
        self.menu.entryconfig(1, label='取消置顶' if topmost else '窗口置顶')
        background_color = self.get_value_from_registry('background_color', '#000000', write=True)
        self.config(bg=background_color)
        self.datetime_label.config(bg=background_color)
        self.note_label.config(bg=background_color)
        self.text_label.config(bg=background_color)
        self.locked = self.get_value_from_registry('lock', False)
        self.toggle_lock_button(False if self.locked else True)
        self.toggle_unlock_button(True if self.locked else False)
        self.text_label.configure(text=self.get_value_from_registry('text_label', '小锋学长生活大爆炸', write=True))
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        win_x = (screen_width - self.window_width) // 2
        win_y = (screen_height - self.window_height) // 2
        x = self.get_value_from_registry('win_x', str(win_x))
        y = self.get_value_from_registry('win_y', str(win_y))
        self.geometry('{}x{}+{}+{}'.format(self.window_width, self.window_height, x, y))

    def init_config_to_registry(self, first=False):
        self.set_value_to_registry('start_date', '2023/2/20')
        self.set_value_to_registry('end_date', '2023/7/9')
        self.set_value_to_registry('startup', None)
        self.set_value_to_registry('topmost', None)
        self.set_value_to_registry('background_color', '#000000')
        self.set_value_to_registry('lock', None)
        self.set_value_to_registry('text_label', '小锋学长生活大爆炸')

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.set_value_to_registry('win_x', str(x))
        self.set_value_to_registry('win_y', str(y))

        if not first:
            messagebox.showinfo("提示", "重启生效")



    
    def check_version(self):
        url = 'http://xfxuezhang.cn/web/share/version/desktop_clock.txt'
        try:
            resp = requests.get(url, timeout=2).text.strip()
            if resp != VERSION:
                if messagebox.askyesno('更新提示', '发现新版本，是否前往蓝奏云下载？密码:c9o1'):
                    webbrowser.open('https://xfxuezhang.lanzouo.com/b09ubrasb')
        except:
            pass


    def get_value_from_registry(self, query, default=None, write=False, vtype=winreg.REG_SZ):
        # 从注册表中读取参数，如果没有，则使用默认值
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CONFIG_REG_PATH, access=winreg.KEY_READ) as key:
                value = winreg.QueryValueEx(key, query)[0]
        except:
            value = default
            if write:
                # 将默认值存储到注册表中
                with winreg.CreateKey(winreg.HKEY_CURRENT_USER, CONFIG_REG_PATH) as key:
                    winreg.SetValueEx(key, query, 0, vtype, default)
        return value

    def set_value_to_registry(self, query, value=None, vtype=winreg.REG_SZ):
        if value is not None:
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, CONFIG_REG_PATH) as key:
                winreg.SetValueEx(key, query, 0, vtype, value)
        else:
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CONFIG_REG_PATH, access=winreg.KEY_ALL_ACCESS) as key:
                    winreg.DeleteValue(key, query)
            except:
                pass


    def check_startup_enabled(self):
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
            access=winreg.KEY_READ)
        app_path = os.path.abspath(sys.argv[0])
        app_name = os.path.basename(app_path)
        try:
            value, type = winreg.QueryValueEx(key, app_name)
        except WindowsError:
            return False
        return value == app_path
    
    def toggle_startup(self):
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run",
            access=winreg.KEY_ALL_ACCESS)
        app_path = os.path.abspath(sys.argv[0])
        app_name = os.path.basename(app_path)
        if self.check_startup_enabled():
            winreg.DeleteValue(key, app_name)
            self.menu.entryconfig(5, label='开机自启')
            messagebox.showinfo("提示", "已取消开机自启动")
        else:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
            self.menu.entryconfig(5, label='取消自启')
            messagebox.showinfo("提示", "已设置开机自启动")
        key.Close()
        self.set_value_to_registry('startup', '1' if self.check_startup_enabled() else None)


    def about_me(self):
        # webbrowser.open_new_tab('http://www.xfxuezhang.cn')
        messagebox.showinfo("关于", "暂时没什么内容")

    # 选择日期
    def modify_date(self):
        top = tk.Toplevel(self)
        # 获取屏幕尺寸和窗口尺寸，使窗口居中
        screen_width = top.winfo_screenwidth()
        screen_height = top.winfo_screenheight()
        window_width = 175
        window_height = 100
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        top.geometry('{}x{}+{}+{}'.format(window_width, window_height, x, y))
        top.title('选择日期')
        tk.Label(top, text='开始日期：').grid(row=0, column=0)
        start_date = tkcalendar.DateEntry(top, width=12, background='darkblue', foreground='white', date_pattern='yyyy/mm/dd', date=self.start_date, justify='center')
        start_date.grid(row=0, column=1)
        tk.Label(top, text='结束日期：').grid(row=1, column=0)
        end_date = tkcalendar.DateEntry(top, width=12, background='darkblue', foreground='white', date_pattern='yyyy/mm/dd', date=self.end_date, justify='center')
        end_date.grid(row=1, column=1)
    
        def update_dates():
            self.start_date = start_date.get_date().strftime('%Y/%m/%d')
            self.end_date = end_date.get_date().strftime('%Y/%m/%d')
            self.update_note_label()
            top.destroy()
            self.set_value_to_registry('start_date', self.start_date)
            self.set_value_to_registry('end_date', self.end_date)
        
        button = tk.Button(top, text="确定", command=update_dates)
        button.grid(row=2, column=0, columnspan=2, pady=10)
        
    # 窗口置顶
    def topmost_on(self):
        if self.attributes('-topmost'):
            self.attributes('-topmost', False)
            self.menu.entryconfig(1, label='窗口置顶')
        else:
            self.attributes('-topmost', True)
            self.menu.entryconfig(1, label='取消置顶')
        self.set_value_to_registry('topmost', '1' if self.attributes('-topmost') else None)

    # 改变背景色
    def choose_color(self):
        color = askcolor()[1]
        if color:
            self.config(bg=color)
            self.datetime_label.config(bg=color)
            self.note_label.config(bg=color)
            self.text_label.config(bg=color)
            self.set_value_to_registry('background_color', color)

    # 锁定
    def toggle_lock_button(self, show=True):
        if show:
            self.lock_button.place(relx=1, rely=0.85, anchor='e')
        else:
            self.lock_button.place_forget()
    # 解除锁定
    def toggle_unlock_button(self, show=True):
        if show:
            self.unlock_button.place(relx=1, rely=0.85, anchor='e')
        else:
            self.unlock_button.place_forget()
    # 锁定和解除锁定的切换
    def toggle_lock(self):
        if self.locked:
            self.locked = False
            self.toggle_lock_button(True)
            self.toggle_unlock_button(False)
        else:
            self.locked = True
            self.toggle_lock_button(False)
            self.toggle_unlock_button(True)
        self.set_value_to_registry('lock', '1' if self.locked else None)
        # self.set_value_to_registry('winfo_screenwidth', self.winfo_x() - self.mouse_x)


    # 显示右键菜单
    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)

    # 更新日期时间
    def update_datetime(self):
        now = datetime.datetime.now().strftime('%Y-%m-%d     \u270d     %H:%M:%S.%f')[:-4]
        msg = f'{now}'
        self.datetime_label.configure(text=msg)
        self.after(10, self.update_datetime)

    # 更新txt文档内容
    def update_text_label(self):
        now = ''
        if os.path.exists('config.txt'):
            now = open('config.txt', 'r', encoding='utf8').read().strip()
        now = now or self.get_value_from_registry('text_label', '小锋学长生活大爆炸')
        if now:
            self.text_label.configure(text=now)
        # self.after(1000, self.update_text_label)

    def edit_text_labele(self):
        """打开文本输入框并更新内容"""
        # 创建文本输入框并显示默认内容
        note = tkinter.simpledialog.askstring('修改Note', '请输入新的note', initialvalue=self.text_label['text'], parent=self)
        # 如果用户点击确认，则更新文本标签的内容
        if note:
            self.text_label['text'] = note
            self.set_value_to_registry('text_label', note)

    # 更新周次
    def update_note_label(self):
        # 指定日期，格式为 年-月-日
        start_y, start_m, start_d = list(map(int, self.start_date.strip().split('/')))
        end_y, end_m, end_d = list(map(int, self.end_date.strip().split('/')))
        specified_start_date = datetime.date(start_y, start_m, start_d)
        specified_end_date = datetime.date(end_y, end_m, end_d)
        today = datetime.date.today()
        # 计算距离指定日期过了多少周
        start_delta = today - specified_start_date
        num_of_weeks = math.ceil(start_delta.days / 7)
        # 计算距离指定日期剩余多少周
        end_delta = specified_end_date - today
        remain_weeks = math.ceil(end_delta.days / 7)

        msg = f'当前第{num_of_weeks}周, 剩余{remain_weeks}周({end_delta.days}天)'
        self.note_label.configure(text=msg)
        self.after(1000*60, self.update_note_label)

    # 实现窗口拖动
    def on_left_button_down(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y

    # 实现窗口拖动
    def on_left_button_up(self, event):
        x = self.winfo_x() + event.x - self.mouse_x
        y = self.winfo_y() + event.y - self.mouse_y
        self.mouse_x = 0
        self.mouse_y = 0
        self.set_value_to_registry('win_x', str(x))
        self.set_value_to_registry('win_y', str(y))

    # 实现窗口拖动
    def on_mouse_drag(self, event):
        if not self.locked:
            x = self.winfo_x() + event.x - self.mouse_x
            y = self.winfo_y() + event.y - self.mouse_y
            self.geometry('+{}+{}'.format(x, y))

    def on_mouse_leave(self, event):
        self.lock_button.place_forget()
        self.unlock_button.place_forget()

    def on_mouse_enter(self, event):
        if not self.locked:
            self.toggle_lock_button(True)
            self.toggle_unlock_button(False)
        else:
            self.toggle_lock_button(False)
            self.toggle_unlock_button(True)


def process():
    app = TransparentWindow(text_file='text.txt')
    app.mainloop()
    
if __name__ == '__main__':
    process()



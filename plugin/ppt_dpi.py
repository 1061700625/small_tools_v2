import tkinter as tk
from tkinter import ttk
import winreg
from tkinter import messagebox


class App(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.version_maps = {
            "Microsoft  365 ": "16.0",
            "PowerPoint 2019": "16.0",
            "PowerPoint 2016": "16.0",
            "PowerPoint 2013": "15.0",
            "PowerPoint 2010": "14.0",
            "PowerPoint 2007": "12.0",
            "PowerPoint 2003": "11.0",
        }
        self.center_window()
        self.create_widgets()

    def center_window(self):
        width = 250
        height = 200
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.master.geometry(f"{width}x{height}+{x}+{y}")
        self.master.title("PPT改DPI")

    def create_widgets(self):
        self.version_label = tk.Label(self, text="选择Office版本:")
        self.version_label.pack()

        self.version_var = tk.StringVar(self)
        self.version_var.set(list(self.version_maps.keys())[0])

        self.version_combobox = ttk.Combobox(
            self,
            textvariable=self.version_var,
            values=list(self.version_maps.keys()),
            state="readonly"
        )
        self.version_combobox.pack()

        self.value_label = tk.Label(self, text="输入要修改的值:")
        self.value_label.pack(pady=5)

        self.value_entry = tk.Entry(self)
        self.value_entry.insert(0, "96")
        self.value_entry.pack(pady=5)

        self.process_button = tk.Button(self, text="执行修改", command=self.process, width=15)
        self.process_button.pack(pady=5)

        self.quit_button = tk.Button(self, text="退出", command=self.master.destroy, width=15)
        self.quit_button.pack(pady=5)

    def process(self):
        version = self.version_maps.get(self.version_var.get())
        input_value = int(self.value_entry.get())

        # 定义注册表路径和项名
        reg_path = fr"Software\Microsoft\Office\{version}\PowerPoint\Options"
        reg_key = "ExportBitmapResolution"

        try:
            # 打开注册表项
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_ALL_ACCESS)
        except:
            messagebox.showerror("错误", f"注册表项不存在，请检查: {reg_path}")
            return

        try:
            # 尝试获取项的值
            value, reg_type = winreg.QueryValueEx(key, reg_key)
            if reg_type == winreg.REG_DWORD:
                # 如果项存在且类型为DWORD32，修改它的值
                winreg.SetValueEx(key, reg_key, 0, winreg.REG_DWORD, input_value)
            else:
                messagebox.showerror("失败", "注册表项类型不符合要求")
        except FileNotFoundError:
            # 如果项不存在，创建它并设置为DWORD32类型
            winreg.SetValueEx(key, reg_key, 0, winreg.REG_DWORD, input_value)
            # 修改它的值
            winreg.SetValueEx(key, reg_key, 0, winreg.REG_DWORD, input_value)
        messagebox.showinfo("成功 ", "修改后的值 =>" + str(winreg.QueryValueEx(key, reg_key)[0]))
        # 关闭注册表项
        winreg.CloseKey(key)

def process():
    root = tk.Tk()
    app = App(master=root)
    app.mainloop()

if __name__ == "__main__":
    process()
    
    
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image
import os

class ImageCompressorApp:
    def __init__(self, master):
        self.master = master
        master.title("图片批量压缩工具——小锋学长生活大爆炸[xfxuezhang.cn]")
        window_width = 650
        window_height = 400
        master.geometry(f'{window_width}x{window_height}')
        master.resizable(False, False)
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.master.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        style = ttk.Style()
        style.theme_use('clam')  # 使用clam主题

        # 设置不同控件的样式
        style.configure('TButton', background='#E1E1E1', foreground='black', width=20, borderwidth=1)
        style.configure('TEntry', foreground='black', borderwidth=1)
        style.configure('TLabel', foreground='black', background='#E1E1E1')
        style.configure('Horizontal.TProgressbar', background='#5CB85C', thickness=10)

        # 容器框架
        top_frame = ttk.Frame(master, padding=10)
        path_frame = ttk.Frame(master, padding=10)
        button_frame = ttk.Frame(master, padding=10)
        slider_frame = ttk.Frame(master, padding=10)
        action_frame = ttk.Frame(master, padding=20)
        estimate_frame = ttk.Frame(master, padding=10)

        # 布局框架
        for frame in [top_frame, path_frame, button_frame, slider_frame, action_frame, estimate_frame]:
            frame.pack(fill=tk.X, padx=10, pady=5)

        # 单选按钮设置
        self.selection_mode = tk.StringVar(value="folder")
        ttk.Radiobutton(top_frame, text="文件夹", variable=self.selection_mode, value="folder", command=self.clear_and_toggle).pack(side=tk.LEFT)
        ttk.Radiobutton(top_frame, text="图片", variable=self.selection_mode, value="file", command=self.clear_and_toggle).pack(side=tk.LEFT)

        # 路径和后缀输入框
        self.path_entry = ttk.Entry(path_frame, width=40)
        self.path_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.suffix_entry = ttk.Entry(path_frame, width=10)
        self.suffix_entry.insert(0, "new")
        self.suffix_entry.pack(side=tk.LEFT)

        # 按钮配置
        self.folder_button = ttk.Button(button_frame, text="选择文件夹", command=self.browse_folder)
        self.folder_button.pack(side=tk.LEFT, padx=5)
        self.file_button = ttk.Button(button_frame, text="选择图片", command=self.browse_file)
        self.file_button.pack(side=tk.LEFT, padx=5)

        # 滑块配置
        ttk.Label(slider_frame, text="压缩率 (0-100%):").pack(side=tk.LEFT)
        self.quality_slider = ttk.Scale(slider_frame, from_=0, to=100, orient=tk.HORIZONTAL)
        self.quality_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.quality_entry = ttk.Entry(slider_frame, width=4)
        self.quality_entry.pack(side=tk.LEFT)
        ttk.Label(slider_frame, text="缩放率 (0-100%):").pack(side=tk.LEFT)
        self.resize_slider = ttk.Scale(slider_frame, from_=0, to_=100, orient=tk.HORIZONTAL)
        self.resize_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.resize_entry = ttk.Entry(slider_frame, width=4)
        self.resize_entry.pack(side=tk.LEFT)

        # 压缩按钮和进度条
        self.compress_button = ttk.Button(action_frame, text="开始压缩", command=self.start_compression)
        self.compress_button.pack(side=tk.TOP)
        self.progress = ttk.Progressbar(action_frame, orient=tk.HORIZONTAL, mode="determinate", length=500)
        self.progress.pack(fill=tk.X, expand=True)

        # 尺寸估计标签
        self.size_estimate_label = ttk.Label(estimate_frame, text="估计压缩后大小: 未知")
        self.size_estimate_label.pack(side=tk.BOTTOM, pady=(5, 10))

        # 初始化状态
        self.clear_and_toggle()
        self.update_resize_entry(100)
        self.update_quality_entry(100)
        self.resize_slider.set(100)
        self.quality_slider.set(100)
        

    def clear_and_toggle(self):
        self.path_entry.delete(0, tk.END)
        if self.selection_mode.get() == "folder":
            self.folder_button['state'] = 'normal'
            self.file_button['state'] = 'disabled'
        else:
            self.folder_button['state'] = 'disabled'
            self.file_button['state'] = 'normal'

    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.path_entry.insert(0, folder_path)
            self.update_size_estimate()

    def browse_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.jpeg *.png")])
        if file_path:
            self.path_entry.insert(0, file_path)
            self.update_size_estimate()

    def update_quality_entry(self, value):
        self.quality_entry.delete(0, tk.END)
        self.quality_entry.insert(0, int(float(value)))
        self.update_size_estimate()

    def update_resize_entry(self, value):
        self.resize_entry.delete(0, tk.END)
        self.resize_entry.insert(0, int(float(value)))
        self.update_size_estimate()

    def update_size_estimate(self):
        if not self.path_entry.get():
            self.size_estimate_label['text'] = "估计压缩后大小: 请选择文件或文件夹"
            return
        quality_factor = float(self.quality_entry.get()) / 100
        resize_factor = (float(self.resize_entry.get()) / 100) ** 2
        if self.selection_mode.get() == "file" and os.path.isfile(self.path_entry.get()):
            original_size = os.path.getsize(self.path_entry.get())
            estimated_size = original_size * quality_factor * resize_factor
            self.size_estimate_label['text'] = f"估计压缩后大小: {estimated_size / 1024:.2f} KB"
        elif self.selection_mode.get() == "folder" and os.path.isdir(self.path_entry.get()):
            total_size = sum(os.path.getsize(os.path.join(self.path_entry.get(), f)) for f in os.listdir(self.path_entry.get()) if os.path.isfile(os.path.join(self.path_entry.get(), f)))
            estimated_size = total_size * quality_factor * resize_factor
            self.size_estimate_label['text'] = f"估计压缩后总大小: {estimated_size / 1024:.2f} KB"

    def start_compression(self):
        self.compress_button['state'] = 'disabled'
        path = self.path_entry.get()
        suffix = self.suffix_entry.get()
        if not path:
            messagebox.showerror("错误", "请先选择一个文件夹或图片。")
            self.compress_button['state'] = 'enable'
            return
        try:
            quality = int(self.quality_entry.get())
            resize = int(self.resize_entry.get())
        except ValueError:
            messagebox.showerror("错误", "压缩率和缩放率必须是数字")
            self.compress_button['state'] = 'enable'
            return

        if self.selection_mode.get() == "folder" and os.path.isdir(path):
            self.compress_folder(path, quality, resize, suffix)
        elif self.selection_mode.get() == "file" and os.path.isfile(path):
            self.compress_image(path, quality, resize, suffix)
        else:
            messagebox.showerror("错误", "所选路径不符合当前模式，请检查。")
        self.compress_button['state'] = 'enable'

    def compress_folder(self, folder_path, quality, resize_percentage, suffix):
        output_folder = f"{folder_path}_{suffix}"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        total_files = len(files)
        self.progress["maximum"] = total_files
        self.progress["value"] = 0

        for i, img_file in enumerate(files):
            img_path = os.path.join(folder_path, img_file)
            self.compress_image(img_path, quality, resize_percentage, output_folder)
            self.progress["value"] = i + 1
            self.master.update()

        messagebox.showinfo("完成", f"所有图片已压缩完毕，保存在 {output_folder}。")

    def compress_image(self, img_path, quality, resize_percentage, output_folder=None):
        img = Image.open(img_path)
        if resize_percentage != 100:
            new_size = (int(img.width * resize_percentage / 100), int(img.height * resize_percentage / 100))
            img = img.resize(new_size, Image.ANTIALIAS)

        if output_folder is None:
            output_folder = os.path.dirname(img_path)
        base, ext = os.path.splitext(os.path.basename(img_path))
        output_path = os.path.join(output_folder, f"{base}_{self.suffix_entry.get()}{ext}") if self.selection_mode.get() == "file" else os.path.join(output_folder, f"{base}{ext}")

        img.save(output_path, quality=quality)


def process():
    root = tk.Tk()
    app = ImageCompressorApp(root)
    root.mainloop()

if __name__ == "__main__":
    process()

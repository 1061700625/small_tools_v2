import os
import torch
import torch.nn as nn
from torchvision import models, transforms
import cv2
import numpy as np
import PIL
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity
from tkinter import *
from tkinter import filedialog, ttk, messagebox
from tqdm import tqdm
import threading
import webbrowser
import pyperclip
import base64

# 模型字典
model_dict = {
    "ResNet50": models.resnet50,
    "VGG16": models.vgg16,
    "SIFT": "SIFT"
}

# 全局模型变量
model = None

def load_model(model_name, max_keypoints, callback):
    global model
    if model_name == "ResNet50":
        weights = models.ResNet50_Weights.IMAGENET1K_V1
        model = model_dict[model_name](weights=weights)
        model = nn.Sequential(*list(model.children())[:-1])  # 去掉最后一层分类层
    elif model_name == "VGG16":
        weights = models.VGG16_Weights.IMAGENET1K_V1
        model = model_dict[model_name](weights=weights)
        model.classifier = nn.Sequential(*list(model.classifier.children())[:-1])  # 去掉最后一层分类层
    elif model_name == "SIFT":
        model = cv2.SIFT_create(nfeatures=max_keypoints)
    if model_name != "SIFT":
        model.eval()
    callback()

# 图像预处理
preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# 提取图像特征的函数
def extract_features(img_path, model, max_keypoints):
    if isinstance(model, cv2.SIFT):
        img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_COLOR)  # 解决中文路径问题
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        keypoints, descriptors = model.detectAndCompute(gray, None)
        if descriptors is not None and len(descriptors) > max_keypoints:
            descriptors = descriptors[:max_keypoints]  # 只取前max_keypoints个描述子
        return descriptors
    else:
        img = PIL.Image.open(img_path).convert('RGB')
        img = preprocess(img).unsqueeze(0)  # 添加批次维度
        with torch.no_grad():
            features = model(img).squeeze().numpy()
        return features

# 创建图形用户界面
class ImageRetrievalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片检索器")
        
        # 设置图标
        icon_data = """
        iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAAXNSR0IArs4c6QAAArBJREFUOE+F011Ik1Ecx/Hf82zP5qPTNpduzWlqqZhtuSjzwtJlGoVJoAUVCN4IioxHy7AuanTrhaiJDcS3NCTmjaFRmi+QE1MxiWlUokyXs6FrDd/mfIyNTFeo5/ac74c/h3MIHLAYpjpeLA68zOGQUqfTNaTV3mndnRD79RpNtVYmC85RqWIiKIqC3e5AX98oW1GRz9nu9gQYRneEJLfmXC6WJHkUtuQykHPzUF9QYWJipqO0NCvDjXgAhqkJpwP87+2ehsclT2RdV6vr6tuxkZGOMJE/Jie+QWm3gXA6nSbT98jy8nwzwTDPbkUlntJKI0OjdwP9ze3Izc1E7YAR8qQEkASw4tqCrbEVavUZ9PQMg8tFFMEU6dazHuTxtmN6dRbrPlLMfTYhVuSHhuedoNOSwRUHYsOygAj7IlaW7DiWcg4jHX1lBFOsW8sqzeO7gYQPakC6BsJC4ePxp2ipMSA7+xL0+m6PH3c6FvIgIQyGcagyUzHePdj4FwiwjyHaoQEVbgZ+8mGx5eCToAA9dW1IuXgWh0WH0NLcgRB5MAqvCPG4YQpcmu75Z4JkkJGLwBchjMoqOAQqjNnm4b/GQgwe/IQB4NF8GJr1KEwT4UnTlNML8F3+CvGvbizTJ7EkPI/eH9N4ZOz1jF+mTEeiWI73AwMwGAy4GqPAgsli9gJeDw9CIQuDPCTEK3YDARQftyGBeXDMA94vKUFXrX7nDl68aod11uzZXJQI0Bu48d8jlXBpKIxW0I51b0B5I5Xf+eatJ5gRcTAi5e75wsM5flAMmXaAomLdavS1JJ93/f2eqP8oBasvue8Xi4cAVeqb6Kp9WU+UPmy6G5eaqJnmrYa5K2Fw0EEfFBTJwWRVG1h2U00wTLnQ5eKnBIVKsg8s/xxgWXbTNm+trKwsGP0NdrAMfsfqk2IAAAAASUVORK5CYII=
        """
        icon_data = icon_data.strip().replace('\n', '')
        icon_image = PhotoImage(data=base64.b64decode(icon_data))
        self.root.iconphoto(False, icon_image)
        
        # 固定窗口大小
        self.root.geometry("500x700")
        self.root.resizable(False, False)
        
        # 初始化变量
        self.target_img_path = StringVar()
        self.folder_path = StringVar()
        self.threshold = DoubleVar(value=0.9)
        self.top_n = IntVar(value=10)
        self.max_keypoints = IntVar(value=5000)
        self.search_type = StringVar(value="相似度阈值")
        self.model_name = StringVar(value="ResNet50")
        self.stop_search = False
        self.results = []
        
        # 创建控件
        self.create_widgets()
        self.create_right_click_menu()

        # 启动时居中窗口
        self.center_window()
    
    def create_widgets(self):
        # 使用 ttk 样式美化界面
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 10))
        style.configure('TLabel', font=('Helvetica', 10))
        style.configure('TEntry', font=('Helvetica', 10))
        style.configure('TCombobox', font=('Helvetica', 10))

        # 创建说明区
        description_frame = Frame(self.root, padx=10, pady=10)
        description_frame.grid(row=0, column=0, sticky="ew")
        
        description_label = Label(description_frame, text="用法介绍：\n1. 选择目标图片用于检索。\n2. 选择搜索目录用于查找相似图片。\n3. 设置相似度阈值或选择前多少张图片。\n4. 开始搜索。\n本工具由“小锋学长生活大爆炸xfxuezhang.cn”制作提供。", justify=LEFT, anchor=W)
        description_label.pack(fill=X)
        
        # 创建输入和按钮控件
        input_frame = Frame(self.root, padx=10, pady=10)
        input_frame.grid(row=1, column=0, sticky="ew")
        
        Label(input_frame, text="目标图片:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        ttk.Entry(input_frame, textvariable=self.target_img_path, width=40).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="浏览", command=self.browse_image).grid(row=0, column=2, padx=5, pady=5)
        
        Label(input_frame, text="搜索目录:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        ttk.Entry(input_frame, textvariable=self.folder_path, width=40).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="浏览", command=self.browse_folder).grid(row=1, column=2, padx=5, pady=5)
        
        Label(input_frame, text="选择模型:").grid(row=2, column=0, padx=5, pady=5, sticky=W)
        self.model_option = ttk.Combobox(input_frame, textvariable=self.model_name, values=list(model_dict.keys()), state='readonly')
        self.model_option.grid(row=2, column=1, padx=5, pady=5)
        self.model_option.bind("<<ComboboxSelected>>", self.update_model)
        
        Label(input_frame, text="相似度选项:").grid(row=3, column=0, padx=5, pady=5, sticky=W)
        self.search_option = ttk.Combobox(input_frame, textvariable=self.search_type, values=["相似度阈值", "相似度选择前多少张图片"], state='readonly')
        self.search_option.grid(row=3, column=1, padx=5, pady=5)
        self.search_option.bind("<<ComboboxSelected>>", self.update_option)
        
        vcmd = (self.root.register(self.validate_threshold), '%P')
        self.option_value = ttk.Entry(input_frame, textvariable=self.threshold, validate='key', validatecommand=vcmd, width=5)
        self.option_value.grid(row=3, column=2, padx=5, pady=5)
        
        Label(input_frame, text="最大检测点数:").grid(row=4, column=0, padx=5, pady=5, sticky=W)
        self.max_keypoints_entry = ttk.Entry(input_frame, textvariable=self.max_keypoints, width=10)
        self.max_keypoints_entry.grid(row=4, column=1, padx=5, pady=5)
        
        button_frame = Frame(input_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)

        self.start_button = ttk.Button(button_frame, text="开始", command=self.start_search)
        self.start_button.pack(side=LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="停止", command=self.stop_search_func)
        self.stop_button.pack(side=LEFT, padx=5)
        
        # 结果列表和滚动条
        result_frame = Frame(self.root, padx=10, pady=10)
        result_frame.grid(row=2, column=0, sticky="nsew")
        
        self.result_scrollbar = Scrollbar(result_frame)
        self.result_scrollbar.pack(side=RIGHT, fill=Y)
        
        self.result_list = Listbox(result_frame, width=65, height=12, yscrollcommand=self.result_scrollbar.set)
        self.result_list.pack(side=LEFT, fill=BOTH, expand=True)
        self.result_list.bind('<Double-1>', self.open_image)
        self.result_list.bind('<Button-3>', self.show_right_click_menu)
        
        self.result_scrollbar.config(command=self.result_list.yview)
        
        # 搜索进度条
        progress_frame = Frame(self.root, padx=10, pady=10)
        progress_frame.grid(row=3, column=0, sticky="ew")
        
        self.progress_label = ttk.Label(progress_frame, text="0%")
        self.progress_label.pack(side=LEFT)
        
        self.progress = ttk.Progressbar(progress_frame, orient=HORIZONTAL, length=300, mode='determinate')
        self.progress.pack(side=LEFT, fill=X, expand=True)
        
        self.current_file_frame = Frame(self.root, padx=10, pady=10)
        self.current_file_frame.grid(row=4, column=0, sticky="ew")
        
        self.current_file_label = ttk.Label(self.current_file_frame, text="", anchor=W)
        self.current_file_label.pack(fill=X, expand=True)
        
        # 下载提示标签
        self.download_label = ttk.Label(self.root, text="正在加载模型，请稍候...", foreground="red")
        
        # 加载默认模型
        self.update_model()
    
    def create_right_click_menu(self):
        self.right_click_menu = Menu(self.root, tearoff=0)
        self.right_click_menu.add_command(label="复制路径", command=self.copy_path)
        self.right_click_menu.add_command(label="复制名称", command=self.copy_name)
        self.right_click_menu.add_command(label="打开路径", command=self.open_folder)
    
    def show_right_click_menu(self, event):
        try:
            self.selected_index = self.result_list.nearest(event.y)
            self.result_list.selection_clear(0, END)
            self.result_list.selection_set(self.selected_index)
            self.right_click_menu.post(event.x_root, event.y_root)
        finally:
            self.right_click_menu.grab_release()

    def copy_path(self):
        selected_img_filename = self.results[self.selected_index][0]
        full_path = os.path.join(self.folder_path.get(), selected_img_filename)
        pyperclip.copy(full_path)

    def copy_name(self):
        selected_img_filename = self.results[self.selected_index][0]
        pyperclip.copy(selected_img_filename)

    def open_folder(self):
        selected_img_filename = self.results[self.selected_index][0]
        folder_path = os.path.join(self.folder_path.get(), selected_img_filename)
        folder_path = os.path.abspath(os.path.dirname(folder_path))
        webbrowser.open(folder_path)
    
    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def validate_threshold(self, P):
        if P == "":
            return True
        try:
            value = float(P)
            return 0.0 <= value <= 1.0
        except ValueError:
            return False

    def browse_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        self.target_img_path.set(file_path)
    
    def browse_folder(self):
        folder_path = filedialog.askdirectory()
        self.folder_path.set(folder_path)
    
    def update_model(self, event=None):
        self.model_option.config(state="disabled")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="disabled")
        self.download_label.grid(row=5, column=0, columnspan=3, padx=10, pady=10)
        
        # 显示或隐藏最大检测点数输入框
        if self.model_name.get() == "SIFT":
            self.max_keypoints_entry.grid(row=4, column=1, padx=5, pady=5)
        else:
            self.max_keypoints_entry.grid_forget()
        
        threading.Thread(target=load_model, args=(self.model_name.get(), self.max_keypoints.get(), self.model_loaded), daemon=True).start()
    
    def model_loaded(self):
        self.model_option.config(state="readonly")
        self.start_button.config(state="normal")
        self.stop_button.config(state="normal")
        self.download_label.grid_forget()
    
    def update_option(self, event):
        if self.search_type.get() == "相似度阈值":
            self.option_value.config(textvariable=self.threshold)
        else:
            self.option_value.config(textvariable=self.top_n)
    
    def start_search(self):
        self.stop_search = False
        self.results = []
        self.result_list.delete(0, END)
        self.progress["value"] = 0
        self.progress["maximum"] = len([f for f in os.listdir(self.folder_path.get()) if f.lower().endswith(('png', 'jpg', 'jpeg'))])
        
        self.start_button.config(state="disabled")
        
        if self.search_type.get() == "相似度阈值":
            threshold = self.threshold.get()
            threading.Thread(target=self.search_by_threshold, args=(threshold,), daemon=True).start()
        else:
            top_n = self.top_n.get()
            threading.Thread(target=self.search_top_n, args=(top_n,), daemon=True).start()
    
    def stop_search_func(self):
        self.stop_search = True
        self.start_button.config(state="normal")
        self.update_result_list()
        messagebox.showinfo("提示", "搜索已停止")
    
    def update_result_list(self):
        self.results.sort(key=lambda x: x[1], reverse=True)
        self.result_list.delete(0, END)
        for img_filename, similarity in self.results:
            self.result_list.insert(END, f"图片: {img_filename}, 相似度: {similarity:.4f}")

    def search_by_threshold(self, threshold):
        try:
            target_features = extract_features(self.target_img_path.get(), model, self.max_keypoints.get())
            folder_path = self.folder_path.get()
            image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
            total_files = len(image_files)
            
            for index, img_filename in enumerate(tqdm(image_files, desc="Processing images")):
                if self.stop_search:
                    break
                img_path = os.path.join(folder_path, img_filename)
                img_features = extract_features(img_path, model, self.max_keypoints.get())
                if self.model_name.get() == "SIFT":
                    similarity = self.compute_sift_similarity(target_features, img_features)
                else:
                    similarity = self.compute_deep_similarity(target_features, img_features)
                
                progress_percent = int((index + 1) / total_files * 100)
                self.progress_label.config(text=f"{progress_percent}%")
                self.progress["value"] = index + 1
                self.current_file_label.config(text=f"当前处理文件: {img_filename}, 相似度: {similarity:.4f}")
                
                if similarity >= threshold:
                    self.results.append((img_filename, similarity))
                    self.result_list.insert(END, f"图片: {img_filename}, 相似度: {similarity:.4f}")
                
                self.root.update_idletasks()
            
            if not self.stop_search:
                self.update_result_list()
                messagebox.showinfo("提示", "搜索完成")
        except Exception as e:
            messagebox.showerror("错误", str(e))
        finally:
            self.start_button.config(state="normal")

    def search_top_n(self, top_n):
        try:
            target_features = extract_features(self.target_img_path.get(), model, self.max_keypoints.get())
            folder_path = self.folder_path.get()
            image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg'))]
            total_files = len(image_files)
            
            similarities = []
            for index, img_filename in enumerate(tqdm(image_files, desc="Processing images")):
                if self.stop_search:
                    break
                img_path = os.path.join(folder_path, img_filename)
                img_features = extract_features(img_path, model, self.max_keypoints.get())
                if self.model_name.get() == "SIFT":
                    similarity = self.compute_sift_similarity(target_features, img_features)
                else:
                    similarity = self.compute_deep_similarity(target_features, img_features)
                
                progress_percent = int((index + 1) / total_files * 100)
                self.progress_label.config(text=f"{progress_percent}%")
                self.progress["value"] = index + 1
                self.current_file_label.config(text=f"当前处理文件: {img_filename}, 相似度: {similarity:.4f}")
                
                similarities.append((img_filename, similarity))
            
            if not self.stop_search:
                similarities.sort(key=lambda x: x[1], reverse=True)
                self.results = similarities[:top_n]
                
                self.update_result_list()
                messagebox.showinfo("提示", "搜索完成")
        except Exception as e:
            messagebox.showerror("错误", str(e))
        finally:
            self.start_button.config(state="normal")

    def compute_sift_similarity(self, features1, features2):
        bf = cv2.BFMatcher()
        matches = bf.knnMatch(features1.reshape(-1, 128), features2.reshape(-1, 128), k=2)
        good_matches = [m for m, n in matches if m.distance < (1 - self.threshold.get()) * n.distance]
        return len(good_matches) / len(matches) if matches else 0
    
    def compute_deep_similarity(self, features1, features2):
        return cosine_similarity([features1], [features2])[0][0]
    
    def open_image(self, event):
        selection = self.result_list.curselection()
        if selection:
            index = selection[0]
            img_filename = self.results[index][0]
            img_path = os.path.join(self.folder_path.get(), img_filename)
            webbrowser.open(img_path)

if __name__ == "__main__":
    root = Tk()
    app = ImageRetrievalApp(root)
    root.mainloop()

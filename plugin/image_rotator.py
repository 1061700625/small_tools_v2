import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

import cv2
import numpy as np
def img_crop_process(img):
    try:
        img_cv = np.array(img.convert('L'))
        img_blur = cv2.GaussianBlur(img_cv, (9, 9), 2)
        circles = cv2.HoughCircles(img_blur, cv2.HOUGH_GRADIENT, dp=1, minDist=20,
                                param1=100, param2=40, minRadius=0, maxRadius=0)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            max_circle = max(circles[0, :], key=lambda x: x[2])  # Select the largest circle by radius
        x, y, r = max_circle
        left = max(x - r, 0)
        right = min(x + r, img_cv.shape[1])
        top = max(y - r, 0)
        bottom = min(y + r, img_cv.shape[0])
        # Load the original image in color
        cropped_color_img = img.crop((left, top, right, bottom))
        mask = np.zeros_like(cropped_color_img)
        cv2.circle(mask, (r, r), r, (255, 255, 255), -1)
        cropped_color_img_with_white_bg = np.where(mask == (255, 255, 255), cropped_color_img, (255, 255, 255))
        final_img = Image.fromarray(np.uint8(cropped_color_img_with_white_bg))
        return final_img
    except Exception:
        return img

class ImageRotatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("旋转图像器 by 小锋学长生活大爆炸")
        self.resizable(False, False)
        width = 400
        height = 600
        self.geometry(f'{width}x{height}')
        # 计算屏幕中心坐标
        screen_width = self.winfo_screenwidth()  
        screen_height = self.winfo_screenheight()
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        # 设置窗口中心坐标
        self.geometry('{}x{}+{}+{}'.format(width, height, int(x), int(y)))

        # Initialize source and result directories
        self.source_directory = 'images'
        self.result_directory = 'result'
        self.original_image = None
        self.rotate_value = 0

        # Frame for source directory selection and display
        self.source_frame = tk.Frame(self)
        self.source_frame.pack(fill='x')
        self.select_source_button = tk.Button(self.source_frame, text="选择图像目录", command=self.select_source_directory)
        self.select_source_button.pack(side='left', padx=10, pady=5)
        self.source_directory_label = tk.Label(self.source_frame, text=self.source_directory)
        self.source_directory_label.pack(side='left')

        # Frame for result directory selection and display
        self.result_frame = tk.Frame(self)
        self.result_frame.pack(fill='x')
        self.select_result_button = tk.Button(self.result_frame, text="选择保存目录", command=self.select_result_directory)
        self.select_result_button.pack(side='left', padx=10, pady=5)
        self.result_directory_label = tk.Label(self.result_frame, text=self.result_directory)
        self.result_directory_label.pack(side='left')

        # Image display frame
        self.img_display = tk.Label(self, width=400, height=400)
        self.img_display.pack(expand=True, fill='both')
        
        # Slider for rotation
        self.rotation_slider = tk.Scale(self, from_=0, to=360, length=400, orient="horizontal", command=self.rotate_image)
        self.rotation_slider.pack(fill='x')

        self.button_frame = tk.Frame(self)
        self.button_frame.pack(side='bottom', fill='x')
        self.prev_button = tk.Button(self.button_frame, text="上一张", command=self.load_prev_image)
        self.prev_button.config(height=2, width=10)  
        self.prev_button.pack(expand=True, fill='x', side='left', padx=10, pady=5)
        self.crop_button = tk.Button(self.button_frame, text="自动裁剪", command=self.crop_image)
        self.crop_button.config(height=2, width=10)  # Make the button larger
        self.crop_button.pack(expand=True, fill='x', side='left', padx=10, pady=5)
        # Button to save the image
        self.save_button = tk.Button(self.button_frame, text="保存图片", command=self.save_image)
        self.save_button.config(height=2, width=10)  # Make the button larger
        self.save_button.pack(expand=True, fill='x', side='left', padx=10, pady=5)
        # Next image button 
        self.next_button = tk.Button(self.button_frame, text="下一张", command=self.load_next_image) 
        self.next_button.config(height=2, width=10)  # Make the button larger
        self.next_button.pack(expand=True, fill='x', side='left', padx=10, pady=5)

        # 信息显示标签  
        self.info_label = tk.Label(self, text='')
        self.info_label.config(height=1)
        self.info_label.pack(side='bottom', fill='x')
        
        # Update the display with the first image from the source directory
        self.load_first_image_from_source()

    def show_debug_msg(self, msg):
        self.info_label.config(text=msg)
                               
    def select_source_directory(self):
        directory = filedialog.askdirectory()
        if directory:  # Update the directory only if a choice was made
            self.source_directory = directory
            self.source_directory_label.config(text=self.source_directory)
        self.load_first_image_from_source()

    def select_result_directory(self):
        directory = filedialog.askdirectory()
        if directory:  # Update the directory only if a choice was made
            self.result_directory = directory
            self.result_directory_label.config(text=self.result_directory)
        
    def load_next_image(self):
        if self.original_image:
            img_files = [f for f in os.listdir(self.source_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
            curr_idx = img_files.index(self.img_name)
            next_idx = curr_idx + 1 if curr_idx < len(img_files) - 1 else 0
            next_img_name = img_files[next_idx]
            self.original_image = Image.open(os.path.join(self.source_directory, next_img_name))
            self.show_debug_msg(f"当前图片[{next_idx+1}/{len(img_files)}]: {os.path.join(self.source_directory, next_img_name)}")
            self.image = self.original_image
            self.img_name = next_img_name
            self.rotation_slider.set(0)
            self.update_image_display()
    
    def load_prev_image(self):
        if self.original_image:
            img_files = [f for f in os.listdir(self.source_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
            curr_idx = img_files.index(self.img_name)
            prev_idx = curr_idx - 1 if curr_idx > 0 else len(img_files) - 1
            prev_img_name = img_files[prev_idx]
            self.original_image = Image.open(os.path.join(self.source_directory, prev_img_name))
            self.show_debug_msg(f"当前图片[{prev_idx+1}/{len(img_files)}]: {os.path.join(self.source_directory, prev_img_name)}")
            self.image = self.original_image
            self.img_name = prev_img_name
            self.rotation_slider.set(0)
            self.update_image_display()
        
    def load_first_image_from_source(self):
        try:
            img_lists = [f for f in os.listdir(self.source_directory) if f.endswith(('.png', '.jpg', '.jpeg'))]
            self.img_name = img_lists[0] if img_lists else None
            if self.img_name:
                self.original_image = Image.open(os.path.join(self.source_directory, self.img_name))
                self.image = self.original_image
                self.show_debug_msg(f"当前图片[{1}/{len(img_lists)}]: {os.path.join(self.source_directory, self.img_name)}")
            else:
                self.original_image = None
                self.image = None
            self.update_image_display()
        except FileNotFoundError:
            self.original_image = None
            self.image = None
            self.img_display.config(image='')
            self.show_debug_msg(f"'{self.source_directory}'路径下没有图片.")

    def rotate_image(self, value):
        if self.original_image:
            angle = int(value)
            self.rotate_value = angle
            self.image = self.original_image.rotate(-angle, resample=Image.Resampling.BILINEAR, fillcolor=(255, 255, 255))
            self.update_image_display()

    def crop_image(self):
        if self.original_image:
            self.original_image = img_crop_process(self.original_image)
            self.rotation_slider.set(0)
            self.update_image_display(self.original_image)

    def update_image_display(self, src_img=None):
        src_img = src_img or self.image
        if src_img:
            # 缩放图片
            image_w, image_h = src_img.size
            if image_w > 400 or image_h > 400: 
                src_img.thumbnail((400,400))
            self.tk_image = ImageTk.PhotoImage(src_img)
            self.img_display.config(image=self.tk_image)
        else:
            self.img_display.config(image='')

    def save_image(self):
        if self.image:
            # Save the rotated image to the selected result directory
            save_path = os.path.join(self.result_directory, self.img_name.split('.')[0] + f'_{self.rotate_value}.' + self.img_name.split('.')[1])
            self.image.save(save_path)
            self.show_debug_msg(f"图片保存成功: {save_path}")
        else:
            self.show_debug_msg("没有图片要保存.")

# Create the 'images' and 'result' directories if they don't exist
os.makedirs('images', exist_ok=True)
os.makedirs('result', exist_ok=True)

# Run the app
app = ImageRotatorApp()
app.mainloop()

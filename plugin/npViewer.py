import sys
import tkinter as tk
from tkinter import filedialog
import numpy as np
import scipy.sparse

'''
pip install scipy
'''

class Viewer:
    def __init__(self) -> None:
        pass

    def load_npy_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Numpy files", "*.npz"), ("Numpy files", "*.npy"),])
        if file_path:
            self.path_input.delete(0, tk.END)  # Clear previous path
            self.path_input.insert(0, file_path)

    def display_npy_content(self):
        file_path = self.path_input.get()
        file_extension = file_path.split('.')[-1].lower()
        try:
            np_array = "Unsupported file format."
            if file_extension == 'npy':
                np_array = np.load(file_path)
            elif file_extension == 'npz':
                np_array = scipy.sparse.load_npz(file_path)
            self.output_text.delete("1.0", tk.END)  # Clear previous output
            self.output_text.insert(tk.END, np_array)
        except Exception as e:
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"Error loading npy file:\n{str(e)}")

    

    def ui(self):
        # Create the main window
        root = tk.Tk()
        root.title("npy/npz文件查看器")

        # Create widgets
        path_label = tk.Label(root, text="npy/npz文件路径")
        path_label.pack()

        self.path_input = tk.Entry(root, width=50)
        self.path_input.pack()

        select_button = tk.Button(root, text="选择npy/npz文件", command=self.load_npy_file)
        select_button.pack()

        display_button = tk.Button(root, text="显示内容", command=self.display_npy_content)
        display_button.pack()

        self.output_text = tk.Text(root, height=20, width=60)
        self.output_text.pack()

        root.mainloop()

def display_npy_content_cmd(file_path):
    file_extension = file_path.split('.')[-1].lower()
    try:
        np_array = "Unsupported file format."
        if file_extension == 'npy':
            np_array = np.load(file_path)
        elif file_extension == 'npz':
            np_array = scipy.sparse.load_npz(file_path)
        print(np_array)
    except Exception as e:
        print(e)

def process():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        display_npy_content_cmd(file_path)
    else:
        Viewer().ui()

    
if __name__ == '__main__':
    process()

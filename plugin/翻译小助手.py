import keyboard
import pyperclip
import time
import tkinter as tk
from tkinter import ttk
from deep_translator import GoogleTranslator
import re
import threading
import os
from infi.systray import SysTrayIcon
import webbrowser
import tempfile
import urllib.request
# from win10toast import ToastNotifier

'''
https://xfxuezhang.blog.csdn.net/article/details/148242601

python -m venv temp
.\temp\\Scripts\activate
pip install pyperclip keyboard deep-translator infi.systray  # pystray pillow win10toast

nuitka --windows-console-mode=disable --onefile --enable-plugin=tk-inter --windows-icon-from-ico=favicon.ico --remove-output --enable-plugin=no-qt --noinclude-pytest-mode=nofollow --output-dir=build/ trans.py
'''
double_press_interval = 0.5
last_c_time = 0
c_press_count = 0
RESOURCE_URLS = {
    "favicon.ico": "https://cccimg.com/down.php/5677882439758d82edccd357b2b00db7.ico",
    "favicon.png": "https://cccimg.com/down.php/f0a755974ef6efd0cd5ff8069589e328.png"
}
RESOURCE_PATHS = {}

# def show_startup_notification():
#     notifier = ToastNotifier()
#     notifier.show_toast(
#         "✅ 翻译助手已启动",
#         "按 Ctrl+C+C 翻译剪贴板；右键托盘图标退出；Esc 键退出",
#         duration=2,
#         threaded=True
#     )

def ensure_resources_exist():
    tmp_dir = tempfile.gettempdir()
    for filename, url in RESOURCE_URLS.items():
        local_path = os.path.join(tmp_dir, filename)
        if not os.path.exists(local_path):
            try:
                print(f"Downloading {filename} ...")
                urllib.request.urlretrieve(url, local_path)
                print(f"Saved: {local_path}")
            except Exception as e:
                print(f"Error {filename}: {e}")
                local_path = None
        RESOURCE_PATHS[filename] = local_path
        
def show_popup(title, message, color="#4caf50"):
    popup = tk.Tk()
    popup.title(title)
    popup.geometry("300x160")
    popup.resizable(False, False)
    x = (popup.winfo_screenwidth() - 300) // 2
    y = (popup.winfo_screenheight() - 160) // 2
    popup.geometry(f"+{x}+{y}")
    popup.attributes('-topmost', True)
    
    popup.iconbitmap(RESOURCE_PATHS.get("favicon.ico"))
    frame = ttk.Frame(popup, padding=20)
    frame.pack(fill="both", expand=True)

    style = ttk.Style()
    style.configure("TLabel", font=("Arial", 12), foreground=color)

    label_msg = ttk.Label(frame, text=message, wraplength=360, justify="center")
    label_msg.pack()

    ttk.Button(frame, text="确定", command=popup.destroy).pack(pady=15)
    popup.mainloop()

def clean_broken_lines(text):
    text = re.sub(r'(\w+)-\n(\w+)', r'\1-\2', text)
    lines = text.split('\n')
    cleaned_lines = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if i < len(lines) - 1 and not re.search(r'[.!?]"?$|:$', stripped):
            cleaned_lines.append(stripped + ' ')
        else:
            cleaned_lines.append(stripped + '\n')
    return ''.join(cleaned_lines).strip()

def translate(text):
    try:
        return GoogleTranslator(source='en', target='zh-CN').translate(text)
    except Exception as e:
        return f"翻译失败: {e}"

def show_translation_window(original_text):
    def on_translate():
        input_text = text_input.get("1.0", tk.END).strip()
        translated = translate(input_text)
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, translated)

    def on_copy():
        translated = text_output.get("1.0", tk.END).strip()
        pyperclip.copy(translated)

    win = tk.Tk()
    win.title("🔤 剪贴板翻译助手 (by 小锋学长生活大爆炸xfxuezhang.cn)")
    win.geometry("720x500")
    win.minsize(500, 300)
    x = (win.winfo_screenwidth() - 720) // 2
    y = (win.winfo_screenheight() - 500) // 2
    win.geometry(f"+{x}+{y}")
    win.attributes('-topmost', True)
    win.iconbitmap(RESOURCE_PATHS.get("favicon.ico"))
    win.focus_force()

    style = ttk.Style()
    style.configure("TLabel", font=("Arial", 11))
    style.configure("TButton", font=("Arial", 11), padding=6)
    text_font = ("Consolas", 11)

    label_input = ttk.Label(win, text="📋 原文：")
    label_input.pack(anchor="w", padx=10, pady=(10, 2))

    text_input = tk.Text(win, font=text_font, wrap="word", bg="#f7f7f7", height=10)
    text_input.pack(fill="both", expand=True, padx=10)
    text_input.insert(tk.END, original_text)

    label_output = ttk.Label(win, text="🌐 翻译结果：")
    label_output.pack(anchor="w", padx=10, pady=(10, 2))

    text_output = tk.Text(win, font=text_font, wrap="word", bg="#f7f7f7", height=10)
    text_output.pack(fill="both", expand=True, padx=10)
    text_output.insert(tk.END, translate(original_text))

    button_frame = ttk.Frame(win)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="🔄 重新翻译", command=on_translate).pack(side="left", padx=12)
    ttk.Button(button_frame, text="📋 复制翻译内容", command=on_copy).pack(side="left", padx=12)

    win.bind('<Escape>', lambda e: win.destroy())
    win.mainloop()

def on_key_event(event):
    global last_c_time, c_press_count
    if keyboard.is_pressed('ctrl') and event.name == 'c' and event.event_type == 'down':
        current_time = time.time()
        if current_time - last_c_time < double_press_interval:
            c_press_count += 1
        else:
            c_press_count = 1
        last_c_time = current_time
        if c_press_count == 2:
            try:
                content = pyperclip.paste()
                # 忽略非文本（如图像）或空字符串
                if not isinstance(content, str) or not content.strip():
                    print("⚠️ 剪贴板内容为空或不是文本，已忽略。")
                    return
                cleaned = clean_broken_lines(content)
                show_translation_window(cleaned)
            except Exception as e:
                print("❌ 错误:", e)
            c_press_count = 0

def run_systray():
    def on_quit(systray): os._exit(0)
    def open_help_page(systray): webbrowser.open("https://xfxuezhang.blog.csdn.net/article/details/148242601")
    menu_options = (("📘 使用说明", None, open_help_page),)
    systray = SysTrayIcon(RESOURCE_PATHS.get("favicon.ico"), "翻译助手", menu_options, on_quit=on_quit)
    systray.start()

def run():
    try:
        ensure_resources_exist()
        keyboard.hook(on_key_event)
        threading.Thread(target=run_systray, daemon=True).start()
        show_popup("翻译助手已启动 ✅", "- 按 Ctrl+C+C 翻译剪贴板; \n- 右键托盘图标退出; \n- Esc 键关闭翻译窗口")
        # show_startup_notification()
        keyboard.wait()
    except Exception as e:
        show_popup("翻译助手异常退出 ❌", f"错误信息：{e}", color="#f44336")
        raise

if __name__ == "__main__":
    run()

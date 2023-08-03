import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import threading
import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.ttk as ttk
import tkinter.simpledialog as simpledialog

def search(keyword):
    filterDisciplines = [
        'animal-science-and-veterinary',
        'biology-and-biochemistry',
        'business-and-management',
        'chemistry',
        'computer-science',
        'earth-science',
        'ecology-and-evolution',
        'economics-and-finance',
        'electronics-and-electrical-engineering',
        'environmental-sciences',
        'genetics-and-molecular-biology',
        'immunology',
        'law-and-political-science',
        'materials-science',
        'mathematics',
        'mechanical-and-aerospace-engineering',
        'medicine',
        'microbiology',
        'neuroscience',
        'physics',
        'plant-science-and-agronomy',
        'psychology',
        'social-sciences-and-humanities',    
    ]

    results = []
    for target in tqdm(filterDisciplines, desc='挨个搜索中...', ncols=60):
        url = 'https://research.com/conference-rankings/' + target

        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.82',
        }
        data = {"searchQuery": keyword}
        soup = BeautifulSoup(requests.post(url, json=data, headers=headers).text, 'lxml')
        
        conference_items = soup.find_all('div', class_='conference-item')
        if not conference_items:
            continue
        
        for item in conference_items:    
            rank = item.find(class_='position').getText().replace('Rank', '').strip()
            score = item.find(class_='rankings-info').getText().strip()
            url = item.find('a').get('href').strip()
            title = item.find('a').getText().strip()
            results.append((rank, title, score, url))
        break

    print('排名\t名称\t\t影响因子\t链接')
    for rank, title, score, url in results:
        print(f'{rank}\t{title}\t{score}\t{url}')

    return results


def on_button_click():
    processing = False
    def perform_search(keyword):
        nonlocal processing
        processing = True
        button.config(text="搜索中...", state=tk.DISABLED)
        
        # Clear the output list before performing the search
        output_listbox.delete(*output_listbox.get_children())

        if keyword is not None and len(keyword.strip()) > 0:
            keyword = keyword.strip()
            for rank, title, score, url in search(keyword):
                output_listbox.insert("", "end", values=(rank, title, score, url))
        processing = False
        button.config(text="开始搜索", state=tk.NORMAL)
    
    if not processing:
        keyword = input_entry.get()
        if not keyword.strip():
            msgbox.showinfo("Warning", "请先输入搜索词")
        else:
            t = threading.Thread(target=perform_search, args=[keyword,], daemon=True)
            t.start()

def on_treeview_double_click(event):
    item = output_listbox.selection()
    if item:
        selected_item = output_listbox.item(item, "values")
        if selected_item:
            link = selected_item[3]
            root.clipboard_clear()
            root.clipboard_append(link)
            msgbox.showinfo("Copy", f"Link copied: {link}")


# 粗糙版本，请勿模仿
root = None
output_listbox = None
input_entry = None
button = None
def process():
    global root, output_listbox, input_entry, button
    root = tk.Tk()
    root.title("Research-er")
    # Calculate the center position of the screen
    window_width = 400
    window_height = 300
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_position = (screen_width - window_width) // 2
    y_position = (screen_height - window_height) // 2
    root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")


    input_entry = tk.Entry(root)
    input_entry.pack(pady=10)

    button = tk.Button(root, text="开始搜索", command=on_button_click)
    button.pack()

    columns = ("Rank", "Name", "Impact Factor", "Link")
    output_listbox = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        output_listbox.heading(col, text=col)
        output_listbox.column(col, width=100, anchor="center")
    output_listbox.pack(pady=10, fill=tk.BOTH, expand=True)

    # Add horizontal and vertical scrollbars to the output listbox
    h_scrollbar = ttk.Scrollbar(root, orient=tk.HORIZONTAL, command=output_listbox.xview)
    v_scrollbar = ttk.Scrollbar(root, orient=tk.VERTICAL, command=output_listbox.yview)
    output_listbox.configure(xscrollcommand=h_scrollbar.set, yscrollcommand=v_scrollbar.set)
    h_scrollbar.pack(fill=tk.X, side=tk.BOTTOM)
    v_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)

    output_listbox.bind("<Double-Button-1>", on_treeview_double_click)

    root.mainloop()


if __name__ == '__main__':
    process()


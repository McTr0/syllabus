import tkinter as tk
from tkinter import ttk

# 创建主窗口和布局
def create_main_window():
    root = tk.Tk()
    root.title("教学计划编制系统")

    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    win_w = min(1400, max(1000, sw - 60))
    win_h = min(900, max(700, sh - 80))
    root.geometry(f"{win_w}x{win_h}")

    paned = tk.PanedWindow(root, orient=tk.VERTICAL, sashrelief=tk.RAISED, sashwidth=5)
    paned.pack(fill=tk.BOTH, expand=True)

    canvas_frame = tk.Frame(paned)
    paned.add(canvas_frame, minsize=200, stretch="always")

    hbar = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
    hbar.pack(side=tk.BOTTOM, fill=tk.X)
    vbar = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
    vbar.pack(side=tk.RIGHT, fill=tk.Y)

    canvas = tk.Canvas(canvas_frame, width=800, height=600, bg='white', xscrollcommand=hbar.set, yscrollcommand=vbar.set)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    hbar.config(command=canvas.xview)
    vbar.config(command=canvas.yview)

    bottom_frame = tk.Frame(paned)
    paned.add(bottom_frame, minsize=100, stretch="never")

    notebook = ttk.Notebook(bottom_frame)
    notebook.pack(fill=tk.BOTH, expand=True)

    # 学期表tab
    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text='学期表')

    # 课程管理tab
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text='课程管理')

    # 设置tab字体大小
    style = ttk.Style()
    style.configure('TNotebook.Tab', font=('Arial', 14))
    style.configure('TFrame', font=('Arial', 12))

    # 默认让上方课程图区域占约 74% 高度
    def _set_initial_sash():
        h = paned.winfo_height()
        if h > 300:
            paned.sash_place(0, 0, int(h * 0.74))

    root.after(80, _set_initial_sash)

    return root, canvas, tab1, tab2, notebook

# 创建学期表UI
def create_semester_table(tab1, num_semesters=8):
    # 策略开关
    tk.Label(tab1, text='均匀分配学期数:', font=('Arial', 12)).grid(row=0, column=0, sticky='w')
    entry = tk.Entry(tab1, font=('Arial', 12), width=5)
    entry.insert(0, str(num_semesters))
    entry.grid(row=0, column=1, sticky='w')

    # 学期表显示
    labels = []
    for i in range(num_semesters):
        label = tk.Label(tab1, text=f'学期 {i+1}:', anchor='w', font=('Arial', 14, 'bold'))
        label.grid(row=1, column=i, sticky='nw')
        labels.append([])
        for j in range(6):
            course_label = tk.Label(tab1, text='', anchor='w', width=20, font=('Arial', 12))
            course_label.grid(row=2+j, column=i, sticky='w')
            labels[i].append(course_label)

    return entry, labels

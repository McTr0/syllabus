from data import load_data, save_data
from graph import build_graph, layout_nodes
from gui import create_main_window, create_semester_table
from logic import set_completed_recursive, assign_courses_to_semesters, update_semester_table
import tkinter as tk
from tkinter import ttk
import networkx as nx
import json

# 加载数据
courses, completed = load_data()
G = build_graph(courses)
node_positions, scroll_x, scroll_y = layout_nodes(courses, G)

save_path = 'data.json'

# 创建GUI
root, canvas, tab1, tab2, notebook = create_main_window()
entry, labels = create_semester_table(tab1)

# 创建菜单栏
menubar = tk.Menu(root)
root.config(menu=menubar)

# 文件菜单
file_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="文件", menu=file_menu)
file_menu.add_command(label="导入", command=lambda: import_data())
file_menu.add_command(label="保存", command=lambda: save_to_file())

# 帮助菜单
help_menu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="帮助", menu=help_menu)
help_menu.add_command(label="使用说明", command=lambda: show_help())

# 设置滚动区域
canvas.config(scrollregion=(0, 0, scroll_x, scroll_y))

# 绘制节点
node_items = {}
for cid, pos in node_positions.items():
    x, y = pos
    if cid in completed:
        fill_color = 'lightgreen'
    elif all(pr in completed for pr in courses[cid]['prerequisites']):
        fill_color = 'yellow'
    else:
        fill_color = 'white'
    rect = canvas.create_rectangle(x-80, y-20, x+80, y+20, fill=fill_color, outline='black')
    text = canvas.create_text(x, y, text=courses[cid]['name'], font=('Arial', 10))
    circle = canvas.create_oval(x+85, y-15, x+105, y+15, fill='white', outline='black')
    num_text = canvas.create_text(x+95, y, text='', font=('Arial', 10))
    node_items[cid] = {'rect': rect, 'text': text, 'circle': circle, 'num': num_text}

# 绘制边
edge_items = {}
for u, v in G.edges():
    x1, y1 = node_positions[u]
    x2, y2 = node_positions[v]
    line_id = canvas.create_line(x1+80, y1, x2-80, y2, arrow=tk.LAST, fill='gray')
    edge_items[(u, v)] = line_id

# 当前显示的课程
current_cid = None
semesters = [[] for _ in range(8)]

def on_entry_change():
    if current_cid:
        update_schedule()

entry.bind('<KeyRelease>', lambda e: on_entry_change())

# 课程管理tab内容
course_listbox = tk.Listbox(tab2, font=('Arial', 12))
course_listbox.pack(side=tk.LEFT, fill=tk.Y, expand=True)
for cid, c in courses.items():
    course_listbox.insert(tk.END, f"{c['name']} ({cid})")

# 右侧Frame
right_frame = tk.Frame(tab2)
right_frame.pack(side=tk.RIGHT, fill=tk.Y)

tk.Label(right_frame, text='课程名:', font=('Arial', 12)).grid(row=0, column=0, sticky='w')
name_entry = tk.Entry(right_frame, font=('Arial', 12))
name_entry.grid(row=0, column=1, sticky='ew')

tk.Label(right_frame, text='前置课程 (逗号分隔ID):', font=('Arial', 12)).grid(row=1, column=0, sticky='w')
prereq_entry = tk.Entry(right_frame, font=('Arial', 12))
prereq_entry.grid(row=1, column=1, sticky='ew')

# 下方按钮
button_frame = tk.Frame(right_frame)
button_frame.grid(row=2, column=0, columnspan=2, pady=10)

search_btn = tk.Button(button_frame, text='查找', command=lambda: search_course())
search_btn.pack(side=tk.LEFT, padx=5)

add_btn = tk.Button(button_frame, text='添加', command=lambda: add_course())
add_btn.pack(side=tk.LEFT, padx=5)

delete_btn = tk.Button(button_frame, text='删除', command=lambda: delete_course())
delete_btn.pack(side=tk.LEFT, padx=5)

def update_schedule():
    if current_cid:
        ancestors = nx.ancestors(G, current_cid)
        ancestors.add(current_cid)
        topo_ancestors = ancestors - completed
        topo_subgraph = G.subgraph(topo_ancestors)
        topo = list(nx.topological_sort(topo_subgraph))
        semesters = assign_courses_to_semesters(topo, int(entry.get()) if entry.get().isdigit() else 8)
        update_semester_table(labels, semesters, courses, len(labels))

# 点击事件
def on_click(event):
    global current_cid
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    
    for items in node_items.values():
        canvas.itemconfig(items['num'], text='')
        canvas.itemconfig(items['circle'], fill='white')
    
    # 设置所有边为灰色
    for line_id in edge_items.values():
        canvas.itemconfig(line_id, fill='gray')
    
    clicked_cid = None
    for cid, items in node_items.items():
        circle = items['circle']
        x1, y1, x2, y2 = canvas.coords(circle)
        if x1 <= x <= x2 and y1 <= y <= y2:
            clicked_cid = cid
            break
        
        rect = items['rect']
        rx1, ry1, rx2, ry2 = canvas.coords(rect)
        if rx1 <= x <= rx2 and ry1 <= y <= ry2:
            new_state = cid not in completed
            set_completed_recursive(cid, new_state, courses, completed, node_items, canvas, G)
            save_data(courses, completed, save_path)
            if current_cid:
                ancestors = nx.ancestors(G, current_cid)
                ancestors.add(current_cid)
                subgraph = G.subgraph(ancestors)
                topo_ancestors = ancestors - completed
                topo_subgraph = G.subgraph(topo_ancestors)
                topo = list(nx.topological_sort(topo_subgraph))
                for i, node in enumerate(topo, 1):
                    if node in node_items:
                        canvas.itemconfig(node_items[node]['num'], text=str(i))
                        canvas.itemconfig(node_items[node]['circle'], fill='yellow')
                # 隐藏所有边
                for line_id in edge_items.values():
                    canvas.itemconfig(line_id, state='hidden')
                for u, v in subgraph.edges():
                    if (u, v) in edge_items:
                        canvas.itemconfig(edge_items[(u, v)], state='normal', fill='red')
                semesters = assign_courses_to_semesters(topo, int(entry.get()) if entry.get().isdigit() else 8)
                update_semester_table(labels, semesters, courses, len(labels))
            return
    
    if clicked_cid:
        current_cid = clicked_cid
        ancestors = nx.ancestors(G, clicked_cid)
        ancestors.add(clicked_cid)
        subgraph = G.subgraph(ancestors)
        topo_ancestors = ancestors - completed
        topo_subgraph = G.subgraph(topo_ancestors)
        topo = list(nx.topological_sort(topo_subgraph))
        for i, node in enumerate(topo, 1):
            if node in node_items:
                canvas.itemconfig(node_items[node]['num'], text=str(i))
                canvas.itemconfig(node_items[node]['circle'], fill='yellow')
        # 隐藏所有边
        for line_id in edge_items.values():
            canvas.itemconfig(line_id, state='hidden')
        for u, v in subgraph.edges():
            if (u, v) in edge_items:
                canvas.itemconfig(edge_items[(u, v)], state='normal', fill='red')
        semesters = assign_courses_to_semesters(topo, int(entry.get()) if entry.get().isdigit() else 8)
        update_semester_table(labels, semesters, courses, len(labels))
    
    else:
        current_cid = None
        for line_id in edge_items.values():
            canvas.itemconfig(line_id, state='normal', fill='gray')
        semesters = [[] for _ in range(8)]
        update_semester_table(labels, semesters, courses, len(labels))

canvas.bind('<Button-1>', on_click)

def on_mousewheel(event):
    canvas.yview_scroll(-event.delta // 120, 'units')

canvas.bind('<MouseWheel>', on_mousewheel)

def search_course():
    name = name_entry.get().strip()
    for i in range(course_listbox.size()):
        item = course_listbox.get(i)
        if name in item:
            course_listbox.selection_clear(0, tk.END)
            course_listbox.selection_set(i)
            course_listbox.see(i)
            break

def add_course():
    name = name_entry.get().strip()
    prereqs_str = prereq_entry.get().strip()
    if not name:
        return
    prereqs = [p.strip() for p in prereqs_str.split(',') if p.strip()]
    # 自动分配ID
    max_num = 0
    for cid in courses.keys():
        if cid.startswith('C') and cid[1:].isdigit():
            num = int(cid[1:])
            max_num = max(max_num, num)
    new_id = f'C{max_num + 1:03d}' if max_num > 0 else 'C001'
    # 计算level
    max_level = 0
    for pr in prereqs:
        if pr in courses:
            max_level = max(max_level, courses[pr]['level'])
    level = max_level + 1 if prereqs else 0
    # 添加课程
    courses[new_id] = {'id': new_id, 'name': name, 'level': level, 'prerequisites': prereqs}
    G.add_node(new_id, **courses[new_id])
    for pr in prereqs:
        if pr in courses:
            G.add_edge(pr, new_id)
    # 更新布局
    global node_positions
    node_positions = layout_nodes(courses, G)[0]
    canvas.config(scrollregion=(0, 0, layout_nodes(courses, G)[1], layout_nodes(courses, G)[2]))
    # 绘制新节点
    x, y = node_positions[new_id]
    fill_color = 'yellow' if all(pr in completed for pr in prereqs) else 'white'
    rect = canvas.create_rectangle(x-80, y-20, x+80, y+20, fill=fill_color, outline='black')
    text = canvas.create_text(x, y, text=name, font=('Arial', 10))
    circle = canvas.create_oval(x+85, y-15, x+105, y+15, fill='white', outline='black')
    num_text = canvas.create_text(x+95, y, text='', font=('Arial', 10))
    node_items[new_id] = {'rect': rect, 'text': text, 'circle': circle, 'num': num_text}
    # 绘制新边
    for pr in prereqs:
        if pr in node_positions:
            x1, y1 = node_positions[pr]
            x2, y2 = node_positions[new_id]
            line_id = canvas.create_line(x1+80, y1, x2-80, y2, arrow=tk.LAST, fill='gray')
            edge_items[(pr, new_id)] = line_id
    # 更新Listbox
    course_listbox.insert(tk.END, f"{name} ({new_id})")
    # 保存
    save_data(courses, completed, save_path)
    # 清空输入
    name_entry.delete(0, tk.END)
    prereq_entry.delete(0, tk.END)

def delete_course():
    selection = course_listbox.curselection()
    if not selection:
        return
    index = selection[0]
    item = course_listbox.get(index)
    cid = item.split('(')[-1].strip(')')
    if cid not in courses:
        return
    # 删除
    del courses[cid]
    G.remove_node(cid)
    # 删除节点和边
    if cid in node_items:
        canvas.delete(node_items[cid]['rect'])
        canvas.delete(node_items[cid]['text'])
        canvas.delete(node_items[cid]['circle'])
        canvas.delete(node_items[cid]['num'])
        del node_items[cid]
    for u, v in list(edge_items.keys()):
        if u == cid or v == cid:
            canvas.delete(edge_items[(u, v)])
            del edge_items[(u, v)]
    # 更新布局
    global node_positions
    node_positions = layout_nodes(courses, G)[0]
    canvas.config(scrollregion=(0, 0, layout_nodes(courses, G)[1], layout_nodes(courses, G)[2]))
    # 重新绘制所有
    canvas.delete('all')
    node_items.clear()
    edge_items.clear()
    for cid, pos in node_positions.items():
        x, y = pos
        if cid in completed:
            fill_color = 'lightgreen'
        elif all(pr in completed for pr in courses[cid]['prerequisites']):
            fill_color = 'yellow'
        else:
            fill_color = 'white'
        rect = canvas.create_rectangle(x-80, y-20, x+80, y+20, fill=fill_color, outline='black')
        text = canvas.create_text(x, y, text=courses[cid]['name'], font=('Arial', 10))
        circle = canvas.create_oval(x+85, y-15, x+105, y+15, fill='white', outline='black')
        num_text = canvas.create_text(x+95, y, text='', font=('Arial', 10))
        node_items[cid] = {'rect': rect, 'text': text, 'circle': circle, 'num': num_text}
    for u, v in G.edges():
        x1, y1 = node_positions[u]
        x2, y2 = node_positions[v]
        line_id = canvas.create_line(x1+80, y1, x2-80, y2, arrow=tk.LAST, fill='gray')
        edge_items[(u, v)] = line_id
    # 更新Listbox
    course_listbox.delete(0, tk.END)
    for cid, c in courses.items():
        course_listbox.insert(tk.END, f"{c['name']} ({cid})")
    # 保存
    save_data(courses, completed, save_path)

def import_data():
    from tkinter import filedialog
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        global courses, completed, G, node_positions, save_path
        save_path = file_path
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        courses = {c['id']: c for c in data['courses']}
        completed = set(data.get('completed_courses', []))
        G = build_graph(courses)
        node_positions, scroll_x, scroll_y = layout_nodes(courses, G)
        canvas.config(scrollregion=(0, 0, scroll_x, scroll_y))
        # 重新绘制
        canvas.delete('all')
        node_items.clear()
        edge_items.clear()
        for cid, pos in node_positions.items():
            x, y = pos
            if cid in completed:
                fill_color = 'lightgreen'
            elif all(pr in completed for pr in courses[cid]['prerequisites']):
                fill_color = 'yellow'
            else:
                fill_color = 'white'
            rect = canvas.create_rectangle(x-80, y-20, x+80, y+20, fill=fill_color, outline='black')
            text = canvas.create_text(x, y, text=courses[cid]['name'], font=('Arial', 10))
            circle = canvas.create_oval(x+85, y-15, x+105, y+15, fill='white', outline='black')
            num_text = canvas.create_text(x+95, y, text='', font=('Arial', 10))
            node_items[cid] = {'rect': rect, 'text': text, 'circle': circle, 'num': num_text}
        for u, v in G.edges():
            x1, y1 = node_positions[u]
            x2, y2 = node_positions[v]
            line_id = canvas.create_line(x1+80, y1, x2-80, y2, arrow=tk.LAST, fill='gray')
            edge_items[(u, v)] = line_id
        # 更新Listbox
        course_listbox.delete(0, tk.END)
        for cid, c in courses.items():
            course_listbox.insert(tk.END, f"{c['name']} ({cid})")

def show_help():
    help_text = """
课程修读管理系统使用说明：

1. 课程图：
   - 绿色节点：已修读课程
   - 黄色节点：可直接修读课程
   - 白色节点：未修读课程
   - 点击圆形：显示拓扑路径
   - 点击矩形：切换修读状态

2. 学期表：
   - 输入学期数，点击圆形后自动分配

3. 课程管理：
   - 左侧：课程列表
   - 右侧：输入新课程信息
   - 查找、添加、删除按钮

4. 菜单：
   - 文件 > 导入：导入JSON数据文件
   - 文件 > 保存：保存当前数据（弹出文件选择窗口）（弹出文件选择窗口）
   - 帮助 > 使用说明：显示此说明

注意：修改后会自动保存到当前文件。
"""
    from tkinter import messagebox
    messagebox.showinfo("使用说明", help_text)

def save_to_file():
    from tkinter import filedialog
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        save_data(courses, completed, file_path)
        global save_path
        save_path = file_path  # 更新保存路径

root.mainloop()

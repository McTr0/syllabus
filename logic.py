# 递归设置修读状态
def set_completed_recursive(cid, state, courses, completed, node_items, canvas, G):
    if cid not in courses:
        return
    if state:
        # 设置为已修读
        if cid not in completed:
            completed.add(cid)
            if cid in node_items:
                canvas.itemconfig(node_items[cid]['rect'], fill='lightgreen')
            for pr in courses[cid]['prerequisites']:
                set_completed_recursive(pr, True, courses, completed, node_items, canvas, G)
            # 更新后继课程的颜色
            for succ in G.successors(cid):
                if succ not in completed and all(p in completed for p in courses[succ]['prerequisites']):
                    if succ in node_items:
                        canvas.itemconfig(node_items[succ]['rect'], fill='yellow')
                elif succ not in completed:
                    if succ in node_items:
                        canvas.itemconfig(node_items[succ]['rect'], fill='white')
    else:
        # 设置为未修读
        if cid in completed:
            completed.remove(cid)
        # 计算新颜色
        if cid in node_items:
            if all(pr in completed for pr in courses[cid]['prerequisites']):
                fill = 'yellow'
            else:
                fill = 'white'
            canvas.itemconfig(node_items[cid]['rect'], fill=fill)
        for succ in G.successors(cid):
            set_completed_recursive(succ, False, courses, completed, node_items, canvas, G)
        # 更新前置课程的颜色
        for pr in courses[cid]['prerequisites']:
            if pr not in completed and all(p in completed for p in courses[pr]['prerequisites']):
                if pr in node_items:
                    canvas.itemconfig(node_items[pr]['rect'], fill='yellow')
            elif pr not in completed:
                if pr in node_items:
                    canvas.itemconfig(node_items[pr]['rect'], fill='white')

# 分配课程到学期
def assign_courses_to_semesters(topo, num_semesters):
    total_courses = len(topo)
    avg_per_semester = total_courses // num_semesters
    extra = total_courses % num_semesters
    courses_per_semester = [avg_per_semester] * num_semesters
    for i in range(extra):
        courses_per_semester[i] += 1
    
    semesters = [[] for _ in range(num_semesters)]
    current = 0
    for i, count in enumerate(courses_per_semester):
        semesters[i] = topo[current:current + count]
        current += count
    return semesters

# 更新学期表
def update_semester_table(labels, semesters, courses, num_semesters):
    for i in range(num_semesters):
        for j in range(6):
            if i < len(semesters) and j < len(semesters[i]):
                labels[i][j].config(text=courses[semesters[i][j]]['name'])
            else:
                labels[i][j].config(text='')

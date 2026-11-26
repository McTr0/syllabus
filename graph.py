import networkx as nx

# 构建图
def build_graph(courses):
    G = nx.DiGraph()
    for c in courses.values():
        G.add_node(c['id'], **c)
        for pr in c['prerequisites']:
            G.add_edge(pr, c['id'])
    return G

# 布局节点
def layout_nodes(courses, G):
    levels = {}
    for c in courses.values():
        lvl = c['level']
        if lvl not in levels:
            levels[lvl] = []
        levels[lvl].append(c['id'])

    x_spacing = 250
    y_spacing = 100
    node_positions = {}
    x = 100
    max_x = 100
    max_y = 50
    for lvl in sorted(levels.keys()):
        y = 50
        for cid in levels[lvl]:
            node_positions[cid] = (x, y)
            y += y_spacing
            if y > max_y:
                max_y = y
        x += x_spacing
        if x > max_x:
            max_x = x

    return node_positions, max_x + 100, max_y + 100

import json
import networkx as nx

# 加载数据
def load_data():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    courses = {c['id']: c for c in data['courses']}
    completed = set(data.get('completed_courses', []))
    return courses, completed

# 保存数据
def save_data(courses, completed, filename='data.json'):
    data = {'courses': list(courses.values()), 'completed_courses': list(completed)}
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

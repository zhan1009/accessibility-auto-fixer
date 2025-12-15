# fixer/label_generator.py
import json
import os


def load_icon_map():
    # 使用相对路径，从项目根目录找 rules/icon_map.json
    base_dir = os.path.dirname(os.path.dirname(__file__))
    file_path = os.path.join(base_dir, 'rules', 'icon_map.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


ICON_MAP = load_icon_map()


def generate_aria_label(context: dict) -> str | None:
    # 1. 优先使用 icon 映射表
    icon = context.get('data_icon')
    if icon and icon in ICON_MAP:
        return ICON_MAP[icon]

    # 2. 输入框：根据 placeholder 推断
    if context.get('tag') == 'input' and context.get('placeholder'):
        placeholder = context['placeholder'].lower()
        if '搜索' in placeholder or 'search' in placeholder:
            return '搜索'

    # 3. 按钮类：根据 class 或内容推断
    if context.get('tag') in ['button', 'div'] and context.get('class'):
        classes = ' '.join(context['class']).lower()
        if 'close' in classes or 'dismiss' in classes or 'x' in classes:
            return '关闭'

    # 4. 特殊符号（如 ×）也视为关闭按钮
    text = context.get('text', '').strip()
    if text == '×' or text == 'X':
        return '关闭'

    return None
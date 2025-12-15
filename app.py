# app.py
import gradio as gr
import os
import sys
import subprocess
from playwright.sync_api import sync_playwright


# === 确保 Chromium 已安装 ===
def ensure_chromium_installed():
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            browser.close()
        print("✅ Chromium 已安装")
    except Exception as e:
        if "Executable doesn't exist" in str(e):
            print("📦 正在安装 Chromium（首次启动约需 1~2 分钟）...")
            subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
        else:
            raise e


ensure_chromium_installed()

# === 导入项目模块 ===
from fixer.axe_runner import run_axe_on_html
from fixer.context_extractor import extract_context_from_elem
from fixer.label_generator import generate_aria_label
from bs4 import BeautifulSoup


def auto_fix_aria(html_input: str):
    if not html_input.strip():
        return "", "请输入 HTML"

    full_html = f"<html><body>{html_input}</body></html>"
    soup = BeautifulSoup(full_html, 'html.parser')
    fixed_count = 0
    processed_elements = set()

    try:
        axe_results = run_axe_on_html(full_html)
        violations = axe_results.get('violations', [])
        axe_targets = set()
        for v in violations:
            if v['id'] in ['button-name', 'aria-input-field-name']:
                for node in v['nodes']:
                    target = node['target'][0]
                    elem = soup.select_one(target)
                    if elem and not elem.get('aria-label'):
                        axe_targets.add(elem)
                        processed_elements.add(id(elem))
    except Exception as e:
        return html_input, f"Axe 扫描失败: {str(e)}"

    candidate_tags = ['button', 'input']
    interactive_divs = soup.find_all('div', attrs={'role': lambda x: x and 'button' in x.lower()})

    candidates = []
    for tag in candidate_tags:
        candidates.extend(soup.find_all(tag))
    candidates.extend(interactive_divs)

    all_candidates = []
    for elem in candidates:
        if elem.get('aria-label'):
            continue
        if id(elem) not in processed_elements:
            all_candidates.append(elem)
            processed_elements.add(id(elem))

    elements_to_fix = list(axe_targets) + all_candidates

    for elem in elements_to_fix:
        context = {
            'tag': elem.name,
            'data_icon': elem.get('data-icon'),
            'class': elem.get('class', []),
            'placeholder': elem.get('placeholder') if elem.name == 'input' else None,
            'text': elem.get_text(strip=True),
            'role': elem.get('role')
        }

        label = generate_aria_label(context)
        if label:
            elem['aria-label'] = label
            fixed_count += 1

    body = soup.body
    fixed_html = ''.join(str(child) for child in body.children) if body else html_input

    total_issues = len(axe_targets)
    report_lines = []
    if fixed_count > 0:
        report_lines.append(f"🔧 修复了 {fixed_count} 个元素")
    if total_issues > 0:
        report_lines.append(f"✅ Axe 发现 {total_issues} 个无障碍问题，已全部处理")
    else:
        report_lines.append("ℹ️ Axe 未发现严重问题，但规则引擎仍尝试优化")

    return fixed_html, "\n".join(report_lines)


# === Gradio 界面 ===
demo = gr.Interface(
    fn=auto_fix_aria,
    inputs=gr.Textbox(
        label="输入 HTML 片段",
        lines=8,
        placeholder='<button data-icon="trash"></button>\n<input placeholder="search...">\n<div role="button" class="close-btn">×</div>'
    ),
    outputs=[
        gr.Code(language="html", label="修复后 HTML"),
        gr.Textbox(label="修复报告", lines=4)
    ],
    examples=[
        ['<button data-icon="trash"></button>\n<input placeholder="search...">\n<div role="button" class="close-btn">×</div>']
    ],
    title="无障碍 UI 自动修复工具",
    description="""
    🛠️ 自动为交互元素添加 aria-label，提升无障碍访问能力。
    支持图标按钮、搜索框、关闭按钮等常见场景。
    """
)

if __name__ == "__main__":
    demo.launch()
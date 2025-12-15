# fixer/axe_runner.py
from playwright.sync_api import sync_playwright
import json


def run_axe_on_html(html_content: str):
    """在无头浏览器中运行 axe-core"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        page.set_content(html_content)
        page.add_script_tag(url="https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.7.0/axe.min.js")

        results = page.evaluate("""
            () => {
                return axe.run({
                    runOnly: {
                        type: 'rule',
                        values: ['button-name', 'aria-input-field-name']
                    }
                });
            }
        """)

        browser.close()
        return results
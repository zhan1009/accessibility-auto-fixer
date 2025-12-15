# fixer/context_extractor.py
from bs4 import BeautifulSoup


def extract_context_from_elem(elem):
    soup = BeautifulSoup(str(elem), 'html.parser')
    elem = soup.select_one('button, input, div')
    if not elem:
        return {}

    return {
        'tag': elem.name,
        'text': elem.get_text(strip=True),
        'data_icon': elem.get('data-icon'),
        'class': elem.get('class', []),
        'placeholder': elem.get('placeholder'),
        'has_img': elem.find('img') is not None
    }
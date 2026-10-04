import pytest
from bs4 import BeautifulSoup

# The test assumes the index.html file is served or opened locally.
# Since this is a static page, the test will parse the HTML file and assert content.

@pytest.fixture
def load_html():
    with open('index.html', 'r', encoding='utf-8') as file:
        return file.read()


def test_page_contains_hello_world(load_html):
    soup = BeautifulSoup(load_html, 'html.parser')

    # Check that body text contains only "Hello World" ignoring whitespace
    body_text = soup.body.get_text(strip=True)
    assert body_text == 'Hello World', f"Expected 'Hello World' found '{body_text}'"


def test_no_additional_elements(load_html):
    soup = BeautifulSoup(load_html, 'html.parser')

    # The body should contain only a single NavigableString (text node), no other tags
    children = [child for child in soup.body.children if not (child.name is None and child.strip() == '')]

    # If children contains exactly one string and no other tags
    # We accept only plain text with no spans or divs
    assert len(children) == 1
    # The child should be a string containing 'Hello World'
    child = children[0]
    if hasattr(child, 'name'):  # tags have name attribute
        pytest.fail("Body contains unexpected HTML elements")
    else:
        assert child.strip() == 'Hello World'


def test_page_has_proper_html_structure(load_html):
    soup = BeautifulSoup(load_html, 'html.parser')
    assert soup.html is not None
    assert soup.head is not None
    assert soup.body is not None
    assert soup.title.string == 'Hello World'

import sys
import re
from bs4 import BeautifulSoup

def contains_python_dict(text):
    # Regex pattern to detect simple Python dict-like strings
    pattern = r"\{[^{}]*:[^{}]*\}"
    return re.search(pattern, text) is not None

def main(html_file_path):
    with open(html_file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Extract all text
    texts = soup.stripped_strings
    for line in texts:
        if contains_python_dict(line):
            print("Error: Found Python dictionary in HTML text:", line)
            sys.exit(1)

    print("No Python dictionaries found in HTML.")
    sys.exit(0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_html_dicts.py <html_file>")
        sys.exit(2)
    main(sys.argv[1])

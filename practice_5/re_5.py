import re

def match_a_anything_b(text):
    pattern = r"^a.*b$"
    return bool(re.match(pattern, text))
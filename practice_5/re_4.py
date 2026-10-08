import re

def match_upper_followed_by_lower(text):
    pattern = r"[A-Z][a-z]+"
    return re.findall(pattern, text)
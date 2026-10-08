import re

def match_lowercase_underscore(text):
    pattern = r"[a-z]+_[a-z]+"
    return re.findall(pattern, text)
import re

def replace_space_comma_dot(text):
    pattern = r"[ ,.]"
    return re.sub(pattern, ":", text)
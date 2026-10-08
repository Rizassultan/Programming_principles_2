import re

def camel_to_snake(text):
    pattern = r"(?<!^)(?=[A-Z])"
    return re.sub(pattern, "_", text).lower()
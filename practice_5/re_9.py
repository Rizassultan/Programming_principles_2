import re

def insert_space_capital_words(text):
    pattern = r"(\b[A-Z]|[a-z][A-Z])"
    return re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
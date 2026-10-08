import re

# 1. Matches 'a' followed by zero or more 'b's
def match_a_zero_or_more_b(text):
    pattern = r"ab*"
    return re.findall(pattern, text)
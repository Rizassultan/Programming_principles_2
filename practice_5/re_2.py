import re


# 2. Matches 'a' followed by two to three 'b's
def match_a_two_to_three_b(text):
    pattern = r"ab{2,3}"
    return re.findall(pattern, text)
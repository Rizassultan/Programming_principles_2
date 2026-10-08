import re

def snake_to_camel(text):
    components = text.split("_")
    return components[0] + "".join(x.title() for x in components[1:])
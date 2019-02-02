def reformat(value):
    chars = {"Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "ä": "ae", "ö": "oe", "ü": "ue", "\\": "/"}
    for char in chars:
        value = value.replace(char, chars[char])
    return value

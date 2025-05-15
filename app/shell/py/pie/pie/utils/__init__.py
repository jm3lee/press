def read_utf8(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()


def write_utf8(text, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)

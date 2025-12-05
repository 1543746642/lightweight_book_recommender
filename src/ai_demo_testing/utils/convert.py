import pathlib


def convert_to_utf8():
    base_path = pathlib.Path(__file__).parent.parent / "data"

    for ext in ("*.md", "*.txt"):
        for file in base_path.rglob(ext):
            content = file.read_text(encoding="gbk", errors="ignore")
            file.write_text(content, encoding="utf-8")
            print(f"Converted: {file}")



from pathlib import Path


def iter_documents(data_dir: Path):
    """Read text documents one at a time from a directory."""
    for file_path in sorted(data_dir.glob("*.txt")):
        with file_path.open("r", encoding="utf-8") as file:
            yield file_path.name, file.read()